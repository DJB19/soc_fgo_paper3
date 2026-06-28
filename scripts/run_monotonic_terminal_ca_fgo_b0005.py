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

# Empirical voltage-SOC model fitted from cycle 1
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

# Factor weights
w_prior_soc = 100.0
w_terminal_soc = 100.0
w_dyn = 50.0
w_volt = 5.0
w_prior_q = 0.5

# New monotonic penalty weight.
# This discourages non-physical SOC increase during discharge.
w_mono = 200.0

q_lower = 0.4 * Q_nominal
q_upper = 1.1 * Q_nominal

for stage, cycle_id in selected_cycles.items():
    cycle = df[df["discharge_cycle_id"] == cycle_id].copy()

    time = cycle["time_s"].to_numpy()
    current = cycle["current_a"].to_numpy()
    voltage = cycle["voltage_v"].to_numpy()
    soc_ref = cycle["soc_reference"].to_numpy()
    q_true = float(cycle["capacity_ah"].iloc[0])

    n = len(time)

    soc_init = nominal_cc(time, current, Q_nominal)
    x0 = np.concatenate([soc_init, np.array([Q_nominal])])

    lower_bounds = np.concatenate([np.zeros(n), np.array([q_lower])])
    upper_bounds = np.concatenate([np.ones(n), np.array([q_upper])])

    def residual(x):
        soc = x[:n]
        q_eff = x[-1]

        res = []

        # Initial SOC prior
        res.append(w_prior_soc * (soc[0] - 1.0))

        # Terminal SOC factor for full-discharge experimental cycle
        res.append(w_terminal_soc * (soc[-1] - 0.0))

        # Weak prior on Q
        res.append(w_prior_q * ((q_eff - Q_nominal) / Q_nominal))

        # Dynamic factors
        for k in range(1, n):
            dt_h = (time[k] - time[k - 1]) / 3600.0
            predicted = soc[k - 1] - abs(current[k]) * dt_h / q_eff
            res.append(w_dyn * (soc[k] - predicted))

        # Monotonicity factors:
        # During discharge, SOC should not increase.
        # Penalize only positive increments.
        dsoc = soc[1:] - soc[:-1]
        mono_violation = np.maximum(dsoc, 0.0)
        res.extend(w_mono * mono_violation)

        # Voltage factors
        v_pred = voltage_model(soc)
        res.extend(w_volt * (voltage - v_pred))

        return np.array(res)

    result = least_squares(
        residual,
        x0,
        bounds=(lower_bounds, upper_bounds),
        max_nfev=800,
        verbose=0,
    )

    soc_mono_fgo = np.clip(result.x[:n], 0.0, 1.0)
    q_est = float(result.x[-1])
    soc_cc_nominal = soc_init

    mono_metrics = calc_metrics(soc_mono_fgo, soc_ref)
    cc_metrics = calc_metrics(soc_cc_nominal, soc_ref)

    # Count monotonic violations after optimization
    dsoc_opt = np.diff(soc_mono_fgo)
    num_mono_violations = int(np.sum(dsoc_opt > 1e-6))
    max_soc_increase = float(np.max(dsoc_opt)) if len(dsoc_opt) > 0 else 0.0

    for method, soc_est, metrics, q_est_value in [
        ("Monotonic Terminal-Constrained CA-FGO", soc_mono_fgo, mono_metrics, q_est),
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
            "num_samples": n,
            "num_mono_violations": num_mono_violations if "FGO" in method else np.nan,
            "max_soc_increase": max_soc_increase if "FGO" in method else np.nan,
            "optimizer_cost": result.cost if "FGO" in method else np.nan,
            "optimizer_nfev": result.nfev if "FGO" in method else np.nan,
            "optimizer_success": result.success if "FGO" in method else np.nan,
        })

    plt.figure()
    plt.plot(time, soc_ref, label="Reference SOC")
    plt.plot(time, soc_cc_nominal, "--", label="Nominal-Capacity CC")
    plt.plot(time, soc_mono_fgo, "-.", label="Monotonic Terminal CA-FGO")
    plt.xlabel("Time (s)")
    plt.ylabel("SOC")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: Monotonic Terminal CA-FGO")
    plt.legend()
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_monotonic_terminal_ca_fgo_soc.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(time, soc_cc_nominal - soc_ref, "--", label="Nominal-Capacity CC Error")
    plt.plot(time, soc_mono_fgo - soc_ref, "-.", label="Monotonic Terminal CA-FGO Error")
    plt.xlabel("Time (s)")
    plt.ylabel("SOC Error")
    plt.title(f"B0005 {stage.capitalize()} Cycle {cycle_id}: Monotonic Terminal CA-FGO Error")
    plt.legend()
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_cycle{cycle_id}_monotonic_terminal_ca_fgo_error.png", dpi=300)
    plt.close()

    print(
        f"{stage} cycle {cycle_id}: "
        f"Mono-TCA-FGO RMSE={mono_metrics['rmse']:.6f}, "
        f"Nominal CC RMSE={cc_metrics['rmse']:.6f}, "
        f"Q_true={q_true:.6f}, Q_est={q_est:.6f}, "
        f"Q_err_percent={(q_est - q_true) / q_true * 100.0:.3f}%, "
        f"mono_violations={num_mono_violations}, "
        f"max_soc_increase={max_soc_increase:.6e}, "
        f"success={result.success}, nfev={result.nfev}"
    )

metrics_df = pd.DataFrame(rows)
metrics_df.to_csv(RESULT_DIR / "B0005_monotonic_terminal_ca_fgo_metrics.csv", index=False)

print("Saved: results/B0005_monotonic_terminal_ca_fgo_metrics.csv")
print(metrics_df.to_string(index=False))
