import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

METRICS_PATH = Path("results/B0005_fgo_metrics.csv")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

df = pd.read_csv(METRICS_PATH)

pivot = df.pivot_table(
    index=["stage", "discharge_cycle_id", "capacity_ratio"],
    columns="method",
    values="rmse"
).reset_index()

# Keep chronological order
stage_order = {"early": 0, "middle": 1, "late": 2}
pivot["stage_order"] = pivot["stage"].map(stage_order)
pivot = pivot.sort_values("stage_order")

labels = [
    f"Cycle {int(row.discharge_cycle_id)}\nRatio {row.capacity_ratio:.3f}"
    for _, row in pivot.iterrows()
]

x = range(len(pivot))
width = 0.35

plt.figure()
plt.bar([i - width/2 for i in x], pivot["Nominal-Capacity CC"], width, label="Nominal-Capacity CC")
plt.bar([i + width/2 for i in x], pivot["FGO"], width, label="FGO")

plt.xticks(list(x), labels)
plt.ylabel("RMSE")
plt.title("SOC Estimation RMSE Comparison Across Aging Stages")
plt.legend()
plt.grid(axis="y")
plt.tight_layout()
plt.savefig(FIG_DIR / "B0005_fgo_vs_nominal_cc_rmse.png", dpi=300)
plt.close()

print("Saved: figures/B0005_fgo_vs_nominal_cc_rmse.png")
print(pivot)
