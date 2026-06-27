import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CSV_PATH = Path("data_processed/B0005_discharge_cycles.csv")
SUMMARY_PATH = Path("data_processed/B0005_cycle_summary.csv")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

df = pd.read_csv(CSV_PATH)
summary = pd.read_csv(SUMMARY_PATH)

total_cycles = int(summary["discharge_cycle_id"].max())
selected_cycles = {
    "early": 1,
    "middle": total_cycles // 2,
    "late": total_cycles
}

print("Selected cycles:", selected_cycles)

for stage, cycle_id in selected_cycles.items():
    cycle = df[df["discharge_cycle_id"] == cycle_id].copy()

    if cycle.empty:
        print(f"WARNING: cycle {cycle_id} not found.")
        continue

    capacity = cycle["capacity_ah"].iloc[0]

    # Voltage
    plt.figure()
    plt.plot(cycle["time_s"], cycle["voltage_v"])
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title(f"B0005 {stage.capitalize()} Stage Cycle {cycle_id}: Voltage, Capacity={capacity:.4f} Ah")
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_{stage}_cycle{cycle_id}_voltage.png", dpi=300)
    plt.close()

    # Current
    plt.figure()
    plt.plot(cycle["time_s"], cycle["current_a"])
    plt.xlabel("Time (s)")
    plt.ylabel("Current (A)")
    plt.title(f"B0005 {stage.capitalize()} Stage Cycle {cycle_id}: Current")
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_{stage}_cycle{cycle_id}_current.png", dpi=300)
    plt.close()

    # SOC reference
    plt.figure()
    plt.plot(cycle["time_s"], cycle["soc_reference"])
    plt.xlabel("Time (s)")
    plt.ylabel("Reference SOC")
    plt.title(f"B0005 {stage.capitalize()} Stage Cycle {cycle_id}: Reconstructed SOC")
    plt.grid(True)
    plt.savefig(FIG_DIR / f"B0005_{stage}_cycle{cycle_id}_soc.png", dpi=300)
    plt.close()

    print(f"{stage}: cycle {cycle_id}, capacity={capacity:.4f} Ah, rows={len(cycle)}")

print("Saved aging-stage figures.")
