import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULT_DIR = Path("results")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

df_nominal = pd.read_csv(RESULT_DIR / "B0005_cc_nominal_metrics.csv")
df_fixed = pd.read_csv(RESULT_DIR / "B0005_fgo_metrics.csv")
df_terminal = pd.read_csv(RESULT_DIR / "B0005_terminal_capacity_aware_fgo_metrics.csv")

df_nominal = df_nominal.copy()
df_nominal["method"] = "Nominal-Capacity CC"

df_fixed = df_fixed[df_fixed["method"] == "FGO"].copy()
df_fixed["method"] = "Fixed-Capacity FGO"

df_terminal = df_terminal[
    df_terminal["method"] == "Terminal-Constrained Capacity-Aware FGO"
].copy()
df_terminal["method"] = "Terminal-Constrained CA-FGO"

cols = ["stage", "discharge_cycle_id", "capacity_ratio", "method", "rmse"]

df_all = pd.concat(
    [
        df_nominal[cols],
        df_fixed[cols],
        df_terminal[cols],
    ],
    ignore_index=True,
)

stage_order = {"early": 0, "middle": 1, "late": 2}
df_all["stage_order"] = df_all["stage"].map(stage_order)
df_all = df_all.sort_values(["stage_order", "method"])

df_all.to_csv(RESULT_DIR / "B0005_three_method_rmse_comparison.csv", index=False)

pivot = df_all.pivot_table(
    index=["stage", "discharge_cycle_id", "capacity_ratio", "stage_order"],
    columns="method",
    values="rmse",
).reset_index()

pivot = pivot.sort_values("stage_order")

labels = [
    f"Cycle {int(row.discharge_cycle_id)}\nRatio {row.capacity_ratio:.3f}"
    for _, row in pivot.iterrows()
]

x = list(range(len(pivot)))
width = 0.22

methods = [
    "Nominal-Capacity CC",
    "Fixed-Capacity FGO",
    "Terminal-Constrained CA-FGO",
]

positions = {
    "Nominal-Capacity CC": [i - width for i in x],
    "Fixed-Capacity FGO": x,
    "Terminal-Constrained CA-FGO": [i + width for i in x],
}

plt.figure(figsize=(9, 5))

for method in methods:
    vals = pivot[method].values
    bars = plt.bar(positions[method], vals, width, label=method)
    for bar, val in zip(bars, vals):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.003,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

plt.xticks(x, labels)
plt.ylabel("RMSE")
plt.title("RMSE Comparison of SOC Estimation Methods Across Aging Stages")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()

out_path = FIG_DIR / "B0005_three_method_rmse_comparison.png"
plt.savefig(out_path, dpi=300)
plt.close()

print("Saved figure:", out_path)
print("Saved table:", RESULT_DIR / "B0005_three_method_rmse_comparison.csv")
print()
print(pivot.to_string(index=False))
