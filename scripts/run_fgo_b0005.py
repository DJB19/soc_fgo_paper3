import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import least_squares

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

# Use cycle 1 capacity as nominal capacity.
cycle1 = df[df["discharge_cycle_id"] == 1].copy()
Q_nominal = float(cycle1["capacity_ah"].iloc[0])

print(f"Nominal capacity from cycle 1: {Q_nominal:.6f} Ah")

# ---------------------------------------------------------------------
# Build an empirical voltage-SOC model from cycle 1.
# This is a simple voltage factor model for the first FGO prototype.
# Later, this can be replaced by an OCV-SOC model or an ECM-based voltage model.
# ---------------------------------------------------------------------
soc_train = cycle1["soc_reference"].to_numpy()
voltage_train = cycle1["voltage_v"].to_numpy()

# Sort by SOC for more stable polynomial fitting.
order = np.argsort(soc_train)
soc_train_sorted = soc_train[order]
voltage_train_sorted = voltage_train[order]

poly_degree = 5
poly_coeff = np.polyfit(soc_train_sorted, voltage_train_sorted, poly_degree)

def voltage_model(soc):
    soc = np.clip(soc, 0.0, 1.0)
    return np.polyval(poly_coeff, soc)

def calc_metrics(est, ref):
    err = est - ref
    rmse = np.sqrt(np.mean(err ** 2))
    mae = np.mean(np.abs(err))
    max_error = np.max(np.abs(err))
    std_error = np.std(err)
    mean_error = np.mean(err)
    return rmse, mae, max_error, std_error, mean_error

def nominal_cc(time, current, q_nominal):
    soc = np.zeros(len(time))
    soc[0] = 1.0
    discharged_ah = 0.0

    for k in range(1, len(time)):
        dt_h = (time[k] - time[k - 1]) / 3600.0
        discharged_ah += abs(current[k]) * dt_h
        soc[k] = 1.0 - discharged_ah / q_nominal

    return np.clip(soc, 0.0, 1.0)

rows = []

# Factor weights.
# These weights may be tuned later.
w_prior = 100.0
w_dyn = 50.0
w_volt = 20.0

for stage, cycle_id in selected_cycles.items():
    cycle = df[df["discharge_cycle_id"] == cycle_id].copy()

    if cycle.empty:
        print(f"WARNING: cycle {cycle_id} not found.")
        continue

    time = cycle["time_s"].to_numpy()
    current = cycle["current_a"].to_numpy()
    voltage = cycle["voltage_v"].to_numpy()
    soc_ref = cycle["soc_reference"].to_numpy()
    q_cycle = float(cycle["capacity_ah"].iloc[0])

    n = len(time)

    # Initial guess: nominal-capacity Coulomb Counting.
    soc_init = nominal_cc(time, current, Q_nominal)

    def residual(x):
        res = []

        # Prior factor: initial SOC is assumed to be 1.
        res.append(w_prior * (x[0] - 1.0))

        # Dynamic factors from current integration.
        for k in range(1, n):
            dt_h = (time[k] - time[k - 1]) / 3600.0
            predicted = x[k - 1] - abs(current[k]) * dt_h / Q_nominal
            res.append(w_dyn * (x[k] - predicted))

        # Voltage measurement factors.
        v_pred = voltage_model(x)
        res.extend(w_volt * (voltage - v_pred))

        return np.array(res)

    result = least_squares(
        residual,
        soc_init,
        bounds=(0.0, 1.0),
        max_nfev=200,
        verbose=0,
    )

    soc_fgo = np.clip(result.x, 0.0, 1.0)
    soc_cc_nominal = soc_init

    rmse, mae, max_error, std_error, mean_error = calc_metrics(soc_fgo, soc_ref)
    cc_rmse, cc_mae, cc_max_error, cc_std_error, cc_mean_error = calc_metrics(soc_cc_nominal, soc_ref)

    rows.append({
        "battery_id": "B0005",
        "stage": stage,
        "discharge_cycle_id": cycle_id,
        "cycle_capacity_ah": q_cycle,
        "nominal_capacity_ah": Q_nominal,
        "capacity_ratio": q_cycle / Q_nominal,
        "method": "FGO",
        "rmse": rmse,
        "mae": mae,
        "max_error": max_error,
        "std_error": std_error,
        "mean_error": mean_error,
        "num_samples": n,
        "optimizer_cost": result.cost,
        "optimizer_nfev": result.nfev,
        "optimizer_success": result.success,
    })

    rows.append({
        "battery_id": "B0005",
        "stage": stage,
        "discharge_cycle_id": cycle_id,
        "cycle_capacity_ah": q_cycle,
        "nominal_capacity_ah": Q_nominal,
        "capacity_ratio": q_cycle / Q_nominal,
        "method": "Nominal-Capacity CC",
        "rmse": cc_rmse,
        "mae": cc_mae,
        "max_error": cc_max_error,
        "std_error": cc_std_error,
        "mean_error": cc_mean_error,
        "num_samples": n,
        "optimizer_cost": np.nan,
        "optimizer_nfev": np.nan,
        "optimizer_success": np.nan,
    })

    # SOC comparison figure.
    plt.figure()
    plt.plot(time, soc_ref, label="Reference SOC")
    plt.plot(time, soc_cc_nominal, "--", label="Nominal-Capacity CC")
    plt.plot(time, soc_fgo, "-.", label="FGO")
    plt.xlabel("Time (s)")
    plt.ylabel("SOC")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: SOC Estimation")
    plt.legend()
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_fgo_soc.png", dpi=300)
    plt.close()

    # Error comparison figure.
    plt.figure()
    plt.plot(time, soc_cc_nominal - soc_ref, "--", label="Nominal-Capacity CC Error")
    plt.plot(time, soc_fgo - soc_ref, "-.", label="FGO Error")
    plt.xlabel("Time (s)")
    plt.ylabel("SOC Error")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: SOC Estimation Error")
    plt.legend()
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_fgo_error.png", dpi=300)
    plt.close()

    print(
        f"{stage} cycle {cycle_id}: "
        f"FGO RMSE={rmse:.6f}, Nominal CC RMSE={cc_rmse:.6f}, "
        f"success={result.success}, nfev={result.nfev}"
    )

metrics = pd.DataFrame(rows)
metrics.to_csv(RESULT_DIR / "B0005_fgo_metrics.csv", index=False)

print("Saved:", RESULT_DIR / "B0005_fgo_metrics.csv")
print(metrics)
