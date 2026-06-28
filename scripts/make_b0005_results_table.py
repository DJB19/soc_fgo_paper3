import pandas as pd
from pathlib import Path

RESULT_DIR = Path("results")
OUT_PATH = RESULT_DIR / "B0005_final_results_table.md"

df_nominal = pd.read_csv(RESULT_DIR / "B0005_cc_nominal_metrics.csv")
df_fixed = pd.read_csv(RESULT_DIR / "B0005_fgo_metrics.csv")
df_physical = pd.read_csv(RESULT_DIR / "B0005_physical_ca_fgo_metrics.csv")

# Nominal-capacity CC
df_nominal = df_nominal.copy()
df_nominal["method"] = "Nominal-Capacity CC"
df_nominal["estimated_capacity_ah"] = ""

# Fixed-capacity FGO
df_fixed = df_fixed[df_fixed["method"] == "FGO"].copy()
df_fixed["method"] = "Fixed-Capacity FGO"
df_fixed["estimated_capacity_ah"] = ""

# Physical CA-FGO
df_physical = df_physical[
    df_physical["method"] == "Physically Constrained Capacity-Aware FGO"
].copy()
df_physical["method"] = "Physical CA-FGO"

cols = [
    "stage",
    "discharge_cycle_id",
    "method",
    "cycle_capacity_ah",
    "estimated_capacity_ah",
    "rmse",
    "mae",
    "max_error",
]

df = pd.concat(
    [df_nominal[cols], df_fixed[cols], df_physical[cols]],
    ignore_index=True
)

stage_order = {"early": 0, "middle": 1, "late": 2}
method_order = {
    "Nominal-Capacity CC": 0,
    "Fixed-Capacity FGO": 1,
    "Physical CA-FGO": 2,
}

df["stage_order"] = df["stage"].map(stage_order)
df["method_order"] = df["method"].map(method_order)
df = df.sort_values(["stage_order", "method_order"])

def fmt(x, digits=4):
    if x == "" or pd.isna(x):
        return "-"
    return f"{float(x):.{digits}f}"

lines = []
lines.append("Table X. SOC estimation performance comparison for B0005 under different aging stages.\n")
lines.append("| Stage | Cycle | Method | True Capacity (Ah) | Estimated Capacity (Ah) | RMSE | MAE | Max Error |")
lines.append("|---|---:|---|---:|---:|---:|---:|---:|")

for _, row in df.iterrows():
    lines.append(
        f"| {row['stage']} "
        f"| {int(row['discharge_cycle_id'])} "
        f"| {row['method']} "
        f"| {fmt(row['cycle_capacity_ah'])} "
        f"| {fmt(row['estimated_capacity_ah'])} "
        f"| {fmt(row['rmse'])} "
        f"| {fmt(row['mae'])} "
        f"| {fmt(row['max_error'])} |"
    )

OUT_PATH.write_text("\n".join(lines), encoding="utf-8")

print("Saved:", OUT_PATH)
print()
print(OUT_PATH.read_text(encoding="utf-8"))
