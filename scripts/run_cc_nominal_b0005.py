import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

CSV_PATH = Path("data_processed/B0005_discharge_cycles.csv")
RESULT_DIR = Path("results")
FIG_DIR = Path("figures")

RESULT_DIR.mkdir(exist_ok=True)
FIG_DIR.mkdir(exist_ok=True)

df = pd.read_csv(CSV_PATH)

selected_cycles = {
    "early": 1,
    "middle": 84,
    "late": 168,
}

# Use cycle 1 capacity as nominal capacity
cycle1 = df[df["discharge_cycle_id"] == 1]
Q_nominal = float(cycle1["capacity_ah"].iloc[0])

print(f"Nominal capacity from cycle 1: {Q_nominal:.6f} Ah")

rows = []

def calc_metrics(est, ref):
    err = est - ref
    rmse = np.sqrt(np.mean(err ** 2))
    mae = np.mean(np.abs(err))
    max_error = np.max(np.abs(err))
    std = np.std(err)
    mean_error = np.mean(err)
    return rmse, mae, max_error, std, mean_error

for stage, cycle_id in selected_cycles.items():
    cycle = df[df["discharge_cycle_id"] == cycle_id].copy()

    if cycle.empty:
        print(f"WARNING: cycle {cycle_id} not found.")
        continue

    time = cycle["time_s"].to_numpy()
    current = cycle["current_a"].to_numpy()
    soc_ref = cycle["soc_reference"].to_numpy()
    Q_cycle = float(cycle["capacity_ah"].iloc[0])

    soc_cc_nominal = np.zeros_like(soc_ref)
    soc_cc_nominal[0] = 1.0

    discharged_ah = 0.0

    for k in range(1, len(time)):
        dt_h = (time[k] - time[k - 1]) / 3600.0
        discharged_ah += abs(current[k]) * dt_h
        soc_cc_nominal[k] = 1.0 - discharged_ah / Q_nominal

    soc_cc_nominal = np.clip(soc_cc_nominal, 0.0, 1.0)

    rmse, mae, max_error, std, mean_error = calc_metrics(soc_cc_nominal, soc_ref)

    rows.append({
        "battery_id": "B0005",
        "stage": stage,
        "discharge_cycle_id": cycle_id,
        "cycle_capacity_ah": Q_cycle,
        "nominal_capacity_ah": Q_nominal,
        "capacity_ratio": Q_cycle / Q_nominal,
        "method": "Coulomb Counting with Nominal Capacity",
        "rmse": rmse,
        "mae": mae,
        "max_error": max_error,
        "std_error": std,
        "mean_error": mean_error,
        "num_samples": len(cycle),
    })

    plt.figure()
    plt.plot(time, soc_ref, label="Reference SOC")
    plt.plot(time, soc_cc_nominal, "--", label="CC with Nominal Capacity")
    plt.xlabel("Time (s)")
    plt.ylabel("SOC")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: Reference vs Nominal-Capacity CC")
    plt.legend()
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_cc_nominal_soc.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(time, soc_cc_nominal - soc_ref)
    plt.xlabel("Time (s)")
    plt.ylabel("SOC Error")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: Nominal-Capacity CC Error")
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_cc_nominal_error.png", dpi=300)
    plt.close()

metrics = pd.DataFrame(rows)
metrics.to_csv(RESULT_DIR / "B0005_cc_nominal_metrics.csv", index=False)

print(metrics)
print("Saved:", RESULT_DIR / "B0005_cc_nominal_metrics.csv")
print("Figures saved in:", FIG_DIR)
