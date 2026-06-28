import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULT_PATH = Path("results/multicell_physical_ca_fgo_metrics.csv")
FIG_DIR = Path("figures")
OUT_DIR = Path("results")

FIG_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(RESULT_PATH)

df = df[df["stage"].isin(["middle", "late"])].copy()
df = df[df["method"].isin(["Nominal-Capacity CC", "Physical CA-FGO"])].copy()

battery_order = ["B0005", "B0006", "B0007", "B0018"]
stage_order = {"middle": 0, "late": 1}

df["battery_order"] = df["battery_id"].map({b: i for i, b in enumerate(battery_order)})
df["stage_order"] = df["stage"].map(stage_order)

pivot = df.pivot_table(
    index=["battery_id", "stage", "discharge_cycle_id", "battery_order", "stage_order"],
    columns="method",
    values="rmse",
).reset_index()

pivot = pivot.sort_values(["battery_order", "stage_order"]).reset_index(drop=True)

labels = [
    f"{row.battery_id}\n{row.stage}\ncycle {int(row.discharge_cycle_id)}"
    for _, row in pivot.iterrows()
]

x = list(range(len(pivot)))
width = 0.35

nominal_vals = pivot["Nominal-Capacity CC"].values
physical_vals = pivot["Physical CA-FGO"].values

plt.figure(figsize=(12, 5))
bars1 = plt.bar([i - width/2 for i in x], nominal_vals, width, label="Nominal-Capacity CC")
bars2 = plt.bar([i + width/2 for i in x], physical_vals, width, label="Physical CA-FGO")

for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,
            h + 0.003,
            f"{h:.3f}",
            ha="center",
            va="bottom",
            fontsize=8
        )

plt.xticks(x, labels)
plt.ylabel("RMSE")
plt.title("Multi-Cell RMSE Comparison Across Middle and Late Aging Stages")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()

fig_path = FIG_DIR / "multicell_middle_late_rmse_comparison.png"
csv_path = OUT_DIR / "multicell_middle_late_rmse_comparison.csv"

plt.savefig(fig_path, dpi=300)
plt.close()

pivot.to_csv(csv_path, index=False)

print("Saved figure:", fig_path)
print("Saved data:", csv_path)
print()
print(pivot.to_string(index=False))
