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

cycle1 = df[df["discharge_cycle_id"] == 1].copy()
Q_nominal = float(cycle1["capacity_ah"].iloc[0])

print(f"Nominal capacity from cycle 1: {Q_nominal:.6f} Ah")

# Empirical voltage-SOC model fitted from cycle 1.
# This keeps the voltage factor consistent with previous FGO versions.
soc_train = cycle1["soc_reference"].to_numpy()
voltage_train = cycle1["voltage_v"].to_numpy()

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
    return {
        "rmse": np.sqrt(np.mean(err ** 2)),
        "mae": np.mean(np.abs(err)),
        "max_error": np.max(np.abs(err)),
        "std_error": np.std(err),
        "mean_error": np.mean(err),
    }

def cumulative_discharged_ah(time, current):
    discharged = np.zeros(len(time))
    total = 0.0

    for k in range(1, len(time)):
        dt_h = (time[k] - time[k - 1]) / 3600.0
        total += abs(current[k]) * dt_h
        discharged[k] = total

    return discharged

def soc_from_capacity(discharge_ah, q_eff):
    soc = 1.0 - discharge_ah / q_eff
    return np.clip(soc, 0.0, 1.0)

def nominal_cc(time, current, q_nominal):
    discharge_ah = cumulative_discharged_ah(time, current)
    return soc_from_capacity(discharge_ah, q_nominal)

rows = []

# Weights for scalar capacity optimization.
# Terminal SOC is important for full-discharge cycles.
w_terminal = 100.0

# Voltage factor is useful but not fully aging-aware.
w_volt = 5.0

# Weak prior prevents unrealistic Q while allowing aging.
w_prior_q = 0.1

q_lower = 0.4 * Q_nominal
q_upper = 1.1 * Q_nominal

for stage, cycle_id in selected_cycles.items():
    cycle = df[df["discharge_cycle_id"] == cycle_id].copy()

    time = cycle["time_s"].to_numpy()
    current = cycle["current_a"].to_numpy()
    voltage = cycle["voltage_v"].to_numpy()
    soc_ref = cycle["soc_reference"].to_numpy()
    q_true = float(cycle["capacity_ah"].iloc[0])

    discharge_ah = cumulative_discharged_ah(time, current)

    soc_cc_nominal = soc_from_capacity(discharge_ah, Q_nominal)

    def residual(q_array):
        q_eff = float(q_array[0])
        soc = soc_from_capacity(discharge_ah, q_eff)

        res = []

        # Terminal SOC factor: complete discharge should end near zero SOC.
        res.append(w_terminal * (soc[-1] - 0.0))

        # Weak prior on capacity.
        res.append(w_prior_q * ((q_eff - Q_nominal) / Q_nominal))

        # Voltage factor.
        v_pred = voltage_model(soc)
        res.extend(w_volt * (voltage - v_pred))

        return np.array(res)

    result = least_squares(
        residual,
        x0=np.array([Q_nominal]),
        bounds=(np.array([q_lower]), np.array([q_upper])),
        max_nfev=300,
        verbose=0,
    )

    q_est = float(result.x[0])
    soc_physical_fgo = soc_from_capacity(discharge_ah, q_est)

    physical_metrics = calc_metrics(soc_physical_fgo, soc_ref)
    cc_metrics = calc_metrics(soc_cc_nominal, soc_ref)

    dsoc = np.diff(soc_physical_fgo)
    num_mono_violations = int(np.sum(dsoc > 1e-9))
    max_soc_increase = float(np.max(dsoc)) if len(dsoc) > 0 else 0.0

    for method, soc_est, metrics, q_est_value in [
        ("Physically Constrained Capacity-Aware FGO", soc_physical_fgo, physical_metrics, q_est),
        ("Nominal-Capacity CC", soc_cc_nominal, cc_metrics, np.nan),
    ]:
        rows.append({
            "battery_id": "B0005",
            "stage": stage,
            "discharge_cycle_id": cycle_id,
            "cycle_capacity_ah": q_true,
            "nominal_capacity_ah": Q_nominal,
            "estimated_capacity_ah": q_est_value,
            "capacity_ratio": q_true / Q_nominal,
            "estimated_capacity_ratio": q_est_value / Q_nominal if not np.isnan(q_est_value) else np.nan,
            "capacity_estimation_error_ah": q_est_value - q_true if not np.isnan(q_est_value) else np.nan,
            "capacity_estimation_error_percent": (q_est_value - q_true) / q_true * 100.0 if not np.isnan(q_est_value) else np.nan,
            "method": method,
            "rmse": metrics["rmse"],
            "mae": metrics["mae"],
            "max_error": metrics["max_error"],
            "std_error": metrics["std_error"],
            "mean_error": metrics["mean_error"],
            "num_samples": len(time),
            "num_mono_violations": num_mono_violations if "FGO" in method else np.nan,
            "max_soc_increase": max_soc_increase if "FGO" in method else np.nan,
            "optimizer_cost": result.cost if "FGO" in method else np.nan,
            "optimizer_nfev": result.nfev if "FGO" in method else np.nan,
            "optimizer_success": result.success if "FGO" in method else np.nan,
        })

    plt.figure()
    plt.plot(time, soc_ref, label="Reference SOC")
    plt.plot(time, soc_cc_nominal, "--", label="Nominal-Capacity CC")
    plt.plot(time, soc_physical_fgo, "-.", label="Physical CA-FGO")
    plt.xlabel("Time (s)")
    plt.ylabel("SOC")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: Physically Constrained CA-FGO")
    plt.legend()
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_physical_ca_fgo_soc.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(time, soc_cc_nominal - soc_ref, "--", label="Nominal-Capacity CC Error")
    plt.plot(time, soc_physical_fgo - soc_ref, "-.", label="Physical CA-FGO Error")
    plt.xlabel("Time (s)")
    plt.ylabel("SOC Error")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: Physically Constrained CA-FGO Error")
    plt.legend()
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_physical_ca_fgo_error.png", dpi=300)
    plt.close()

    print(
        f"{stage} cycle {cycle_id}: "
        f"Physical CA-FGO RMSE={physical_metrics['rmse']:.6f}, "
        f"Nominal CC RMSE={cc_metrics['rmse']:.6f}, "
        f"Q_true={q_true:.6f}, Q_est={q_est:.6f}, "
        f"Q_err_percent={(q_est - q_true) / q_true * 100.0:.3f}%, "
        f"mono_violations={num_mono_violations}, "
        f"max_soc_increase={max_soc_increase:.6e}, "
        f"success={result.success}, nfev={result.nfev}"
    )

metrics_df = pd.DataFrame(rows)
metrics_df.to_csv(RESULT_DIR / "B0005_physical_ca_fgo_metrics.csv", index=False)

print("Saved: results/B0005_physical_ca_fgo_metrics.csv")
print(metrics_df.to_string(index=False))
