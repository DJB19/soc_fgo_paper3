import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

METRICS_PATH = Path("results/B0005_cc_nominal_metrics.csv")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

df = pd.read_csv(METRICS_PATH)

plt.figure()
plt.plot(df["capacity_ratio"], df["rmse"], marker="o")
for _, row in df.iterrows():
    plt.annotate(
        f"Cycle {int(row['discharge_cycle_id'])}",
        (row["capacity_ratio"], row["rmse"]),
        textcoords="offset points",
        xytext=(5, 5)
    )

plt.xlabel("Capacity Ratio Relative to Cycle 1")
plt.ylabel("RMSE of Nominal-Capacity CC")
plt.title("Effect of Capacity Degradation on SOC Estimation Error")
plt.grid(True)
plt.savefig(FIG_DIR / "B0005_capacity_ratio_vs_cc_nominal_rmse.png", dpi=300)
plt.close()

print("Saved: figures/B0005_capacity_ratio_vs_cc_nominal_rmse.png")
