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
    "middle": 82,
    "late": 164,
}

rows = []

def calc_metrics(est, ref):
    err = est - ref
    rmse = np.sqrt(np.mean(err ** 2))
    mae = np.mean(np.abs(err))
    max_error = np.max(np.abs(err))
    std = np.std(err)
    return rmse, mae, max_error, std

for stage, cycle_id in selected_cycles.items():
    cycle = df[df["discharge_cycle_id"] == cycle_id].copy()

    if cycle.empty:
        print(f"WARNING: cycle {cycle_id} not found.")
        continue

    time = cycle["time_s"].to_numpy()
    current = cycle["current_a"].to_numpy()
    soc_ref = cycle["soc_reference"].to_numpy()
    capacity = float(cycle["capacity_ah"].iloc[0])

    soc_cc = np.zeros_like(soc_ref)
    soc_cc[0] = 1.0

    discharged_ah = 0.0

    for k in range(1, len(time)):
        dt_h = (time[k] - time[k - 1]) / 3600.0
        discharged_ah += abs(current[k]) * dt_h
        soc_cc[k] = 1.0 - discharged_ah / capacity

    soc_cc = np.clip(soc_cc, 0.0, 1.0)

    rmse, mae, max_error, std = calc_metrics(soc_cc, soc_ref)

    rows.append({
        "battery_id": "B0005",
        "stage": stage,
        "discharge_cycle_id": cycle_id,
        "capacity_ah": capacity,
        "method": "Coulomb Counting",
        "rmse": rmse,
        "mae": mae,
        "max_error": max_error,
        "std_error": std,
        "num_samples": len(cycle),
    })

    plt.figure()
    plt.plot(time, soc_ref, label="Reference SOC")
    plt.plot(time, soc_cc, "--", label="Coulomb Counting SOC")
    plt.xlabel("Time (s)")
    plt.ylabel("SOC")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: Reference vs Coulomb Counting")
    plt.legend()
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_cc_soc.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(time, soc_cc - soc_ref)
    plt.xlabel("Time (s)")
    plt.ylabel("SOC Error")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: Coulomb Counting Error")
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_cc_error.png", dpi=300)
    plt.close()

metrics = pd.DataFrame(rows)
metrics.to_csv(RESULT_DIR / "B0005_cc_metrics.csv", index=False)

print(metrics)
print("Saved:", RESULT_DIR / "B0005_cc_metrics.csv")
print("Figures saved in:", FIG_DIR)
