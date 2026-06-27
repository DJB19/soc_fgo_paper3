import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CSV_PATH = Path("data_processed/B0005_discharge_cycles.csv")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

if not CSV_PATH.exists():
    print(f"ERROR: Cannot find {CSV_PATH}")
    print("Run scripts/parse_nasa_b0005.py first.")
    exit()

df = pd.read_csv(CSV_PATH)

cycle_id = 1
cycle = df[df["discharge_cycle_id"] == cycle_id]

if cycle.empty:
    print(f"ERROR: cycle {cycle_id} not found.")
    exit()

plt.figure()
plt.plot(cycle["time_s"], cycle["voltage_v"])
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title(f"B0005 Discharge Cycle {cycle_id}: Voltage")
plt.grid(True)
plt.savefig(FIG_DIR / f"B0005_voltage_cycle{cycle_id}.png", dpi=300)
plt.close()

plt.figure()
plt.plot(cycle["time_s"], cycle["current_a"])
plt.xlabel("Time (s)")
plt.ylabel("Current (A)")
plt.title(f"B0005 Discharge Cycle {cycle_id}: Current")
plt.grid(True)
plt.savefig(FIG_DIR / f"B0005_current_cycle{cycle_id}.png", dpi=300)
plt.close()

plt.figure()
plt.plot(cycle["time_s"], cycle["soc_reference"])
plt.xlabel("Time (s)")
plt.ylabel("Reference SOC")
plt.title(f"B0005 Discharge Cycle {cycle_id}: Reconstructed SOC")
plt.grid(True)
plt.savefig(FIG_DIR / f"B0005_soc_cycle{cycle_id}.png", dpi=300)
plt.close()

print("Figures saved in figures/")
