import scipy.io
import pandas as pd
import numpy as np
from pathlib import Path

RAW_PATH = Path("data_raw/B0005.mat")
OUT_PATH = Path("data_processed/B0005_discharge_cycles.csv")

def main():
    if not RAW_PATH.exists():
        print(f"ERROR: Cannot find {RAW_PATH}")
        print("Please put B0005.mat into data_raw/ first.")
        return

    mat = scipy.io.loadmat(RAW_PATH)
    battery = mat["B0005"]
    cycles = battery[0, 0]["cycle"][0]

    rows = []
    discharge_count = 0

    for idx, cycle in enumerate(cycles):
        cycle_type = str(cycle["type"][0])

        if cycle_type != "discharge":
            continue

        discharge_count += 1
        data = cycle["data"][0, 0]

        voltage = data["Voltage_measured"][0]
        current = data["Current_measured"][0]
        temperature = data["Temperature_measured"][0]
        time = data["Time"][0]
        capacity = float(data["Capacity"][0, 0])

        soc_ref = []
        discharged_ah = 0.0
        soc_ref.append(1.0)

        for k in range(1, len(time)):
            dt_hours = (time[k] - time[k - 1]) / 3600.0
            discharged_ah += abs(current[k]) * dt_hours
            soc = 1.0 - discharged_ah / capacity
            soc_ref.append(soc)

        soc_ref = np.clip(np.array(soc_ref), 0.0, 1.0)

        for k in range(len(time)):
            rows.append({
                "battery_id": "B0005",
                "cycle_index_raw": idx,
                "discharge_cycle_id": discharge_count,
                "time_s": float(time[k]),
                "voltage_v": float(voltage[k]),
                "current_a": float(current[k]),
                "temperature_c": float(temperature[k]),
                "capacity_ah": capacity,
                "soc_reference": float(soc_ref[k]),
            })

    df = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"Saved: {OUT_PATH}")
    print(f"Total discharge cycles: {discharge_count}")
    print("Rows:", len(df))
    print(df.head())
    print(df.tail())

if __name__ == "__main__":
    main()
