# Paper 3: FGO-Based Battery SOC Estimation Using Public Battery Aging Data

This repository contains scripts, processed data summaries, figures, results, and manuscript drafts for Paper 3.

## Topic

Evaluation of FGO-based battery SOC estimation under aging conditions using public experimental lithium-ion battery datasets.

## Current status

- NASA B0005 battery data processed
- 164 discharge cycles extracted
- Reference SOC reconstructed from discharge capacity
- Capacity degradation curve generated
- Coulomb Counting baseline implemented
- Nominal-capacity Coulomb Counting baseline implemented or under development
- Manuscript draft created up to Section 4

## Directory structure

- `scripts/`: data parsing, plotting, and baseline estimation scripts
- `data_processed/`: processed CSV files and cycle summaries
- `figures/`: generated figures
- `results/`: evaluation metrics
- `manuscript/`: paper draft

## Note

Raw NASA `.mat` files are not included in this repository. Please download them from the official NASA battery aging dataset source.
