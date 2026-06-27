import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

SUMMARY_PATH = Path("data_processed/B0005_cycle_summary.csv")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

summary = pd.read_csv(SUMMARY_PATH)

plt.figure()
plt.plot(summary["discharge_cycle_id"], summary["capacity_ah"], marker="o")
plt.xlabel("Discharge Cycle ID")
plt.ylabel("Measured Capacity (Ah)")
plt.title("B0005 Capacity Degradation Across Discharge Cycles")
plt.grid(True)
plt.savefig(FIG_DIR / "B0005_capacity_degradation.png", dpi=300)
plt.close()

print("Saved: figures/B0005_capacity_degradation.png")
