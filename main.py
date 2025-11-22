import os
from src.data_prep import events_to_matrix, summarize_matrix, save_info
from src.sequential import sequential_best_row
from src.dac import dac_best_row
from src.plots_basic import save_heatmap, save_bar_chart


def main():
    """
    This is the main script that:
    1. Loads the dock event CSV
    2. Builds the occupancy matrix (U)
    3. Runs both Sequential and Divide-and-Conquer algorithms
    4. Saves metadata
    5. Draws the heatmap + bar chart
    Basically this file connects all modules together.
    """

    # Use dynamic paths so the script works even if the project is moved
    base_dir = os.path.dirname(os.path.abspath(__file__))

    input_csv = os.path.join(base_dir, "data", "dock_events_raw_sample.csv")
    output_heatmap = os.path.join(base_dir, "plots", "heatmap.png")
    output_barchart = os.path.join(base_dir, "plots", "bar_chart.png")
    output_info = os.path.join(base_dir, "data", "info.json")

    delta_mins = 5  # slot size in minutes

    # Check if CSV exists before running anything
    if not os.path.exists(input_csv):
        print(f"ERROR: '{input_csv}' not found!")
        print(f"Please put the file here: {base_dir}")
        return

    print("1. Preparing data (building occupancy matrix)...")
    U, docks, slots = events_to_matrix(input_csv, delta_mins)

    # Matrix summary (size, sparsity etc.)
    summary = summarize_matrix(U)
    print(f"   -> Matrix Size: {summary['R']} rows x {summary['T']} columns")
    print(f"   -> Total occupied cells: {summary['ones']}")
    print(f"   -> Sparsity: %{summary['sparsity']*100:.2f}")

    print("\n2. Running Sequential Algorithm...")
    best_idx, max_count = sequential_best_row(U)

    # If we have dock labels, print them too
    if docks:
        best_dock_name = docks[best_idx]
        print(f"   -> RESULT: Busiest dock: {best_dock_name} (ID: {best_idx})")
    else:
        print(f"   -> RESULT: Busiest dock ID: {best_idx}")

    print(f"   -> Occupied for {max_count} time slots.")

    print("\n3. Running Divide-and-Conquer Algorithm...")
    best_idx_dac, max_count_dac = dac_best_row(U)

    if docks:
        best_dock_name_dac = docks[best_idx_dac]
        print(f"   -> RESULT: Busiest dock: {best_dock_name_dac} (ID: {best_idx_dac})")
    else:
        print(f"   -> RESULT: Busiest dock ID: {best_idx_dac}")

    print(f"   -> Occupied for {max_count_dac} time slots.")

    # Check if both algorithms agree (they should!)
    if best_idx == best_idx_dac and max_count == max_count_dac:
        print("\n   ✓ Both algorithms returned the same result!")
    else:
        print("\n   ✗ WARNING: Algorithms gave different results!")

    print("\n4. Saving metadata...")
    save_info(U, delta_mins, output_info)

    print("\n5. Creating plots...")
    save_heatmap(U, output_heatmap)

    # Use dock labels for nicer x-axis names in the bar chart
    save_bar_chart(U, output_barchart, best_dock_idx=best_idx, dock_labels=docks)

    print("   -> Plots saved in 'plots/' folder.")

    print("\n--- PROCESS COMPLETED ---")


if __name__ == "__main__":
    main()
