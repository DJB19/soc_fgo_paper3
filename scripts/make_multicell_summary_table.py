import pandas as pd
from pathlib import Path

RESULT_PATH = Path("results/multicell_physical_ca_fgo_metrics.csv")
OUT_PATH = Path("results/multicell_middle_late_summary_table.md")

df = pd.read_csv(RESULT_PATH)

df = df[df["stage"].isin(["middle", "late"])].copy()

nominal = df[df["method"] == "Nominal-Capacity CC"].copy()
physical = df[df["method"] == "Physical CA-FGO"].copy()

merge_cols = ["battery_id", "stage", "discharge_cycle_id"]

merged = nominal.merge(
    physical,
    on=merge_cols,
    suffixes=("_nominal", "_physical")
)

merged["rmse_reduction_percent"] = (
    1.0 - merged["rmse_physical"] / merged["rmse_nominal"]
) * 100.0

battery_order = {"B0005": 0, "B0006": 1, "B0007": 2, "B0018": 3}
stage_order = {"middle": 0, "late": 1}

merged["battery_order"] = merged["battery_id"].map(battery_order)
merged["stage_order"] = merged["stage"].map(stage_order)
merged = merged.sort_values(["battery_order", "stage_order"])

def fmt(x, digits=4):
    return f"{float(x):.{digits}f}"

lines = []
lines.append("Table Y. Cross-cell SOC estimation performance comparison across middle and late aging stages.\n")
lines.append("| Battery | Stage | Cycle | True Capacity (Ah) | Estimated Capacity (Ah) | Nominal CC RMSE | Physical CA-FGO RMSE | RMSE Reduction (%) |")
lines.append("|---|---|---:|---:|---:|---:|---:|---:|")

for _, row in merged.iterrows():
    lines.append(
        f"| {row['battery_id']} "
        f"| {row['stage']} "
        f"| {int(row['discharge_cycle_id'])} "
        f"| {fmt(row['cycle_capacity_ah_nominal'])} "
        f"| {fmt(row['estimated_capacity_ah_physical'])} "
        f"| {fmt(row['rmse_nominal'])} "
        f"| {fmt(row['rmse_physical'])} "
        f"| {fmt(row['rmse_reduction_percent'], 2)} |"
    )

OUT_PATH.write_text("\n".join(lines), encoding="utf-8")

print("Saved:", OUT_PATH)
print()
print(OUT_PATH.read_text(encoding="utf-8"))
