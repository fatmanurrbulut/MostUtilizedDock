import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os


def save_heatmap(U: np.ndarray, output_path: str = "plots/heatmap.png"):
    """
    Creates a heatmap of the occupancy matrix U.
    Each row is a dock, and each column is a time slot.
    The idea is to visualize when a dock is busy (1) or empty (0).
    """

    # Make sure the folder exists (otherwise saving fails)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(15, 8))

    # seaborn heatmap makes the matrix much easier to read
    ax = sns.heatmap(
        U,
        cmap="viridis",  # color theme
        cbar=True,
        cbar_kws={'label': 'Occupancy (0=Empty, 1=Occupied)', 'shrink': 0.75},
        linewidths=0.1,   # small grid lines
        linecolor='white'
    )

    plt.title("Dock Occupancy Heatmap Over Time", fontsize=18, fontweight='bold')
    plt.xlabel("Time Slots", fontsize=14)
    plt.ylabel("Dock ID (Rows)", fontsize=14)

    # Keep Y labels horizontal (easier to read)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Heatmap saved: {output_path}")


def save_bar_chart(U: np.ndarray, output_path: str = "plots/bar_chart.png",
                   best_dock_idx: int = None, dock_labels: list = None):
    """
    Makes a bar chart for total occupancy per dock.
    Basically counts how many 1s are in each row and shows them as bars.
    If best_dock_idx is given, that bar is highlighted.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Count how many time slots each dock is occupied
    row_counts = np.sum(U, axis=1)

    # If dock labels exist and match the size, use them
    if dock_labels is not None and len(dock_labels) == len(row_counts):
        display_labels = dock_labels
        dock_indices = np.arange(len(row_counts))
    else:
        # Otherwise just use simple 0,1,2,... labels
        display_labels = [str(i) for i in range(len(row_counts))]
        dock_indices = np.arange(len(row_counts))

    plt.figure(figsize=(12, 7))

    # Highlight the best dock (if provided)
    colors = [
        'skyblue' if i != best_dock_idx else 'salmon'
        for i in dock_indices
    ]
    edge_colors = [
        'steelblue' if i != best_dock_idx else 'red'
        for i in dock_indices
    ]

    plt.bar(dock_indices, row_counts, color=colors,
            edgecolor=edge_colors, linewidth=1.2)

    plt.title("Total Occupancy Duration Per Dock", fontsize=18, fontweight='bold')
    plt.xlabel("Dock ID", fontsize=14)
    plt.ylabel("Total Occupied Time Slots", fontsize=14)

    # Rotate labels for readability
    plt.xticks(dock_indices, display_labels, fontsize=12, rotation=45, ha='right')
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    # If we know the max row, show its value on top
    if best_dock_idx is not None:
        offset = max(row_counts) * 0.01
        plt.text(best_dock_idx,
                 row_counts[best_dock_idx] + offset,
                 f"Max: {row_counts[best_dock_idx]}",
                 ha='center', va='bottom',
                 color='red', fontweight='bold', fontsize=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Bar chart saved: {output_path}")
