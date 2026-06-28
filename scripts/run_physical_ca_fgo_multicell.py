import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import least_squares

DATA_DIR = Path("data_processed")
RESULT_DIR = Path("results")
FIG_DIR = Path("figures")

RESULT_DIR.mkdir(exist_ok=True)
FIG_DIR.mkdir(exist_ok=True)

battery_ids = ["B0005", "B0006", "B0007", "B0018"]

def voltage_model_from_cycle1(df):
    cycle1 = df[df["discharge_cycle_id"] == 1].copy()
    soc_train = cycle1["soc_reference"].to_numpy()
    voltage_train = cycle1["voltage_v"].to_numpy()

    order = np.argsort(soc_train)
    soc_train_sorted = soc_train[order]
    voltage_train_sorted = voltage_train[order]

    poly_coeff = np.polyfit(soc_train_sorted, voltage_train_sorted, 5)

    def voltage_model(soc):
        soc = np.clip(soc, 0.0, 1.0)
        return np.polyval(poly_coeff, soc)

    return voltage_model

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

def calc_metrics(est, ref):
    err = est - ref
    return {
        "rmse": np.sqrt(np.mean(err ** 2)),
        "mae": np.mean(np.abs(err)),
        "max_error": np.max(np.abs(err)),
        "std_error": np.std(err),
        "mean_error": np.mean(err),
    }

rows = []

for battery_id in battery_ids:
    csv_path = DATA_DIR / f"{battery_id}_discharge_cycles.csv"
    summary_path = DATA_DIR / f"{battery_id}_cycle_summary.csv"

    df = pd.read_csv(csv_path)
    summary = pd.read_csv(summary_path)

    n_cycles = len(summary)
    selected_cycles = {
        "early": 1,
        "middle": int(round(n_cycles / 2)),
        "late": n_cycles,
    }

    cycle1 = df[df["discharge_cycle_id"] == 1].copy()
    Q_nominal = float(cycle1["capacity_ah"].iloc[0])

    voltage_model = voltage_model_from_cycle1(df)

    print(f"\nBattery {battery_id}: nominal capacity = {Q_nominal:.6f} Ah, cycles = {n_cycles}")
    print("Selected cycles:", selected_cycles)

    for stage, cycle_id in selected_cycles.items():
        cycle = df[df["discharge_cycle_id"] == cycle_id].copy()

        time = cycle["time_s"].to_numpy()
        current = cycle["current_a"].to_numpy()
        voltage = cycle["voltage_v"].to_numpy()
        soc_ref = cycle["soc_reference"].to_numpy()
        q_true = float(cycle["capacity_ah"].iloc[0])

        discharge_ah = cumulative_discharged_ah(time, current)

        soc_nominal = soc_from_capacity(discharge_ah, Q_nominal)

        # Fixed-capacity FGO equivalent in this simplified physical framework:
        # SOC is fixed by nominal capacity, so it is the same trajectory as nominal CC.
        # We keep fixed FGO separately in B0005 only. For cross-cell validation,
        # compare nominal CC against physical CA-FGO.

        w_terminal = 100.0
        w_volt = 5.0
        w_prior_q = 0.1

        q_lower = 0.4 * Q_nominal
        q_upper = 1.1 * Q_nominal

        def residual(q_array):
            q_eff = float(q_array[0])
            soc = soc_from_capacity(discharge_ah, q_eff)

            res = []
            res.append(w_terminal * (soc[-1] - 0.0))
            res.append(w_prior_q * ((q_eff - Q_nominal) / Q_nominal))

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
        soc_physical = soc_from_capacity(discharge_ah, q_est)

        nominal_metrics = calc_metrics(soc_nominal, soc_ref)
        physical_metrics = calc_metrics(soc_physical, soc_ref)

        dsoc = np.diff(soc_physical)
        num_mono_violations = int(np.sum(dsoc > 1e-9))
        max_soc_increase = float(np.max(dsoc)) if len(dsoc) > 0 else 0.0

        for method, soc_est, metrics, q_est_value in [
            ("Nominal-Capacity CC", soc_nominal, nominal_metrics, np.nan),
            ("Physical CA-FGO", soc_physical, physical_metrics, q_est),
        ]:
            rows.append({
                "battery_id": battery_id,
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
        plt.plot(time, soc_nominal, "--", label="Nominal-Capacity CC")
        plt.plot(time, soc_physical, "-.", label="Physical CA-FGO")
        plt.xlabel("Time (s)")
        plt.ylabel("SOC")
        plt.title(f"{battery_id} {stage.capitalize()} Cycle {cycle_id}: Physical CA-FGO")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(FIG_DIR / f"{battery_id}_cycle{cycle_id}_physical_ca_fgo_soc.png", dpi=300)
        plt.close()

        print(
            f"{battery_id} {stage} cycle {cycle_id}: "
            f"Nominal RMSE={nominal_metrics['rmse']:.5f}, "
            f"Physical CA-FGO RMSE={physical_metrics['rmse']:.5f}, "
            f"Q_true={q_true:.5f}, Q_est={q_est:.5f}, "
            f"Q_err={(q_est - q_true) / q_true * 100:.2f}%, "
            f"mono={num_mono_violations}"
        )

metrics_df = pd.DataFrame(rows)
out_path = RESULT_DIR / "multicell_physical_ca_fgo_metrics.csv"
metrics_df.to_csv(out_path, index=False)

print("\nSaved:", out_path)
print(metrics_df.to_string(index=False))
