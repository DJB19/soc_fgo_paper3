import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.io import loadmat

if len(sys.argv) != 2:
    print("Usage: python3 scripts/parse_nasa_battery.py B0005")
    sys.exit(1)

battery_id = sys.argv[1]

RAW_PATH = Path("data_raw") / f"{battery_id}.mat"
OUT_DIR = Path("data_processed")
OUT_DIR.mkdir(exist_ok=True)

if not RAW_PATH.exists():
    raise FileNotFoundError(f"Cannot find {RAW_PATH}")

mat = loadmat(RAW_PATH)

battery = mat[battery_id][0, 0]
cycles = battery["cycle"][0]

all_rows = []
summary_rows = []

discharge_cycle_id = 0

for raw_cycle_id, cycle in enumerate(cycles, start=1):
    cycle_type = str(cycle["type"][0])
    if cycle_type != "discharge":
        continue

    discharge_cycle_id += 1

    data = cycle["data"][0, 0]

    time = data["Time"][0]
    voltage = data["Voltage_measured"][0]
    current = data["Current_measured"][0]
    temperature = data["Temperature_measured"][0]

    capacity = float(data["Capacity"][0, 0])

    # Construct cumulative discharged capacity using measured current.
    discharged_ah = np.zeros(len(time))
    total_ah = 0.0

    for k in range(1, len(time)):
        dt_h = (time[k] - time[k - 1]) / 3600.0
        total_ah += abs(current[k]) * dt_h
        discharged_ah[k] = total_ah

    soc_reference = 1.0 - discharged_ah / capacity
    soc_reference = np.clip(soc_reference, 0.0, 1.0)

    for k in range(len(time)):
        all_rows.append({
            "battery_id": battery_id,
            "raw_cycle_id": raw_cycle_id,
            "discharge_cycle_id": discharge_cycle_id,
            "time_s": time[k],
            "voltage_v": voltage[k],
            "current_a": current[k],
            "temperature_c": temperature[k],
            "capacity_ah": capacity,
            "discharged_ah": discharged_ah[k],
            "soc_reference": soc_reference[k],
        })

    summary_rows.append({
        "battery_id": battery_id,
        "raw_cycle_id": raw_cycle_id,
        "discharge_cycle_id": discharge_cycle_id,
        "capacity_ah": capacity,
        "num_samples": len(time),
        "duration_s": time[-1] - time[0],
        "start_voltage_v": voltage[0],
        "end_voltage_v": voltage[-1],
        "start_temperature_c": temperature[0],
        "end_temperature_c": temperature[-1],
    })

df = pd.DataFrame(all_rows)
summary = pd.DataFrame(summary_rows)

df.to_csv(OUT_DIR / f"{battery_id}_discharge_cycles.csv", index=False)
summary.to_csv(OUT_DIR / f"{battery_id}_cycle_summary.csv", index=False)

print(f"Battery: {battery_id}")
print(f"Discharge cycles extracted: {discharge_cycle_id}")
print(f"Saved: {OUT_DIR / f'{battery_id}_discharge_cycles.csv'}")
print(f"Saved: {OUT_DIR / f'{battery_id}_cycle_summary.csv'}")
print()
print(summary[["discharge_cycle_id", "capacity_ah", "num_samples", "duration_s"]].head())
print("...")
print(summary[["discharge_cycle_id", "capacity_ah", "num_samples", "duration_s"]].tail())
