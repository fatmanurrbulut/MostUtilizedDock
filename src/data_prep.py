import pandas as pd
import numpy as np
import json
import os
from datetime import datetime


def build_time_grid(day_start, day_end, delta_minutes):
    """
    Creates time slots between the start and end of the day.
    Basically we split the whole day into equal pieces using 'delta_minutes'.
    """

    # Using 'min' instead of 'T' because of the new pandas warning
    slots = pd.date_range(start=day_start, end=day_end, freq=f'{delta_minutes}min')

    # Convert pandas timestamps to normal Python datetime objects
    return slots.to_pydatetime().tolist()


def events_to_matrix(csv_path, delta_minutes=5):
    """
    Reads the CSV file and turns the events into a 0/1 occupancy matrix.
    Each row = a dock
    Each column = a time slot
    """

    # --- 1. Read the CSV ---
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]  # remove accidental spaces

    # Convert times to proper datetime format
    df['arrival_time'] = pd.to_datetime(df['arrival_time'])
    df['departure_time'] = pd.to_datetime(df['departure_time'])

    # --- 2. Build the timeline (time slots) ---
    if len(df) > 0:
        # Floor/ceil hours to avoid warnings
        day_start = df['arrival_time'].min().floor('h')
        day_end = df['departure_time'].max().ceil('h')
    else:
        # If CSV is empty, just use full day
        now = datetime.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = now.replace(hour=23, minute=59, second=0, microsecond=0)

    slots = build_time_grid(day_start, day_end, delta_minutes)

    # Get all dock IDs and assign an index to each
    docks = sorted(df['dock_id'].unique()) if 'dock_id' in df.columns else []
    dock_map = {d: i for i, d in enumerate(docks)}

    R = len(docks)   # number of docks
    T = len(slots)   # number of time slots

    # --- 3. Create the empty matrix ---
    U = np.zeros((R, T), dtype=int)

    # --- 4. Fill the matrix with 1s where the dock is occupied ---
    for _, row in df.iterrows():
        if row['dock_id'] in dock_map:

            r = dock_map[row['dock_id']]   # row index

            # Find the start and end time in the slot list
            t_start = np.searchsorted(slots, row['arrival_time'], side='right') - 1
            t_end = np.searchsorted(slots, row['departure_time'], side='left')

            # Make sure they stay inside the valid range
            t_start = max(0, t_start)
            t_end = min(T, t_end)

            # Fill that range with 1s (occupied)
            if t_start < t_end:
                U[r, t_start:t_end] = 1

    return U, docks, slots


def summarize_matrix(U):
    """
    Returns some basic statistics about the occupancy matrix.
    Things like: number of docks, number of time slots, how many 1s, sparsity, etc.
    """
    R, T = U.shape

    total_ones = int(np.sum(U))
    total_cells = R * T

    # sparsity = how empty the matrix is
    sparsity = 1.0 - (total_ones / total_cells) if total_cells > 0 else 0.0

    return {
        "R": R,
        "T": T,
        "ones": total_ones,
        "sparsity": sparsity
    }


def save_info(U, delta_minutes, output_path="data/info.json"):
    """
    Saves the summary info into a JSON file.
    This helps us remember the matrix size and density later.
    """

    # Create folder if it doesn’t exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    summary = summarize_matrix(U)

    info = {
        "R": summary["R"],
        "T": summary["T"],
        "ones": summary["ones"],
        "sparsity": round(summary["sparsity"], 4),
        "delta": delta_minutes
    }

    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    print(f"Meta bilgisi kaydedildi: {output_path}")
    return info
