# Paper 3: FGO-Based SOC Estimation Using Public Battery Aging Data

This repository contains scripts, processed data, figures, results, and manuscript drafts for Paper 3.

## Topic

**Evaluation of FGO-based battery SOC estimation under aging conditions using public experimental lithium-ion battery datasets.**

This study uses public NASA lithium-ion battery aging data to evaluate SOC estimation methods under capacity degradation. The main objective is to investigate whether factor graph optimization (FGO) can improve SOC estimation when battery capacity changes due to aging.

## Dataset

The project uses the NASA lithium-ion battery aging dataset.

The following cells are used:

| Battery | Discharge cycles | First capacity (Ah) | Last capacity (Ah) |
|---|---:|---:|---:|
| B0005 | 168 | 1.8565 | 1.3251 |
| B0006 | 168 | 2.0353 | 1.1857 |
| B0007 | 168 | 1.8911 | 1.4325 |
| B0018 | 132 | 1.8550 | 1.3411 |

Raw `.mat` files are not included in this repository. They are excluded by `.gitignore`.

## Methods

The current experiments compare the following methods:

1. **Nominal-Capacity Coulomb Counting**
   - Uses the first-cycle capacity as a fixed nominal capacity.
   - Shows increasing SOC error as the battery ages.

2. **Fixed-Capacity FGO**
   - Uses nominal capacity and adds a voltage-related factor.
   - Provides limited improvement because capacity is still fixed.

3. **Physically Constrained Capacity-Aware FGO**
   - Estimates an effective capacity.
   - Generates SOC from cumulative discharged capacity.
   - Enforces a monotonic SOC decrease during discharge.
   - Provides the main proposed method in this study.

## Main Results

For B0005:

| Stage | Cycle | Nominal CC RMSE | Physical CA-FGO RMSE |
|---|---:|---:|---:|
| Middle | 84 | 0.1041 | 0.0089 |
| Late | 168 | 0.1881 | 0.0196 |

Cross-cell validation was also conducted on B0006, B0007, and B0018. The physically constrained capacity-aware FGO consistently reduced SOC estimation error in the middle and late aging stages across all tested cells.

## Repository Structure

```text
.
 data_raw/
   └── Raw NASA .mat files, ignored by Git
 data_processed/
   ├── B0005_discharge_cycles.csv
   ├── B0005_cycle_summary.csv
 B0006_discharge_cycles.csv   ├
   ├── B0006_cycle_summary.csv
 B0007_discharge_cycles.csv   
   ├── B0007_cycle_summary.csv
   ├── B0018_discharge_cycles.csv
 B0018_cycle_summary.csv   └
 figures/
   ├── B0005 capacity degradation and SOC estimation figures
   ├── Physical CA-FGO SOC estimation figures
   └── Multicell RMSE comparison figures
 results/
   ├── B0005 baseline and FGO metrics
   ├── multicell_physical_ca_fgo_metrics.csv
   └── summary tables
 scripts/
   ├── parse_nasa_battery.py
   ├── run_physical_ca_fgo_multicell.py
   ├── plot_multicell_rmse_comparison.py
 table-generation scripts   
 manuscript/
    └── paper3_draft.md

