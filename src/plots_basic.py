import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

def save_heatmap(U: np.ndarray, output_path: str = "plots/heatmap.png"):
    """
    Plots the occupancy matrix (U) as a colored heatmap.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.figure(figsize=(15, 8))
    
    ax = sns.heatmap(
        U, 
        cmap="viridis", 
        cbar=True, 
        cbar_kws={'label': 'Occupancy (0=Empty, 1=Occupied)', 'shrink': 0.75},
        linewidths=0.1, 
        linecolor='white'
    )
    
    plt.title("Dock Occupancy Heatmap Over Time", fontsize=18, fontweight='bold')
    plt.xlabel("Time Slots", fontsize=14)
    plt.ylabel("Dock ID (Rows)", fontsize=14)
    
    # Y ekseni etiketlerini düz tut
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Heatmap saved: {output_path}")

def save_bar_chart(U: np.ndarray, output_path: str = "plots/bar_chart.png", best_dock_idx: int = None, dock_labels: list = None):
    """
    Plots a bar chart showing the total occupancy duration for each dock.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    row_counts = np.sum(U, axis=1)
    
    # Etiketleri ayarla
    if dock_labels is not None and len(dock_labels) == len(row_counts):
        display_labels = dock_labels
        dock_indices = np.arange(len(row_counts))
    else:
        display_labels = [str(i) for i in np.arange(len(row_counts))]
        dock_indices = np.arange(len(row_counts))

    plt.figure(figsize=(12, 7))
    
    # Renkleri ayarla (Best dock farklı renk)
    colors = ['skyblue' if i != best_dock_idx else 'salmon' for i in dock_indices]
    edge_colors = ['steelblue' if i != best_dock_idx else 'red' for i in dock_indices]

    plt.bar(dock_indices, row_counts, color=colors, edgecolor=edge_colors, linewidth=1.2)
            
    plt.title("Total Occupancy Duration Per Dock", fontsize=18, fontweight='bold')
    plt.xlabel("Dock ID", fontsize=14)
    plt.ylabel("Total Occupied Time Slots", fontsize=14)
    
    # X ekseni etiketlerini döndür ve yerleştir
    plt.xticks(dock_indices, display_labels, fontsize=12, rotation=45, ha='right')
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Max değerini grafiğe yaz
    if best_dock_idx is not None:
        offset = max(row_counts) * 0.01 # Yüksekliği ayarla
        plt.text(best_dock_idx, row_counts[best_dock_idx] + offset, 
                 f'Max: {row_counts[best_dock_idx]}', 
                 ha='center', va='bottom', color='red', fontweight='bold', fontsize=12)
        
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Bar chart saved: {output_path}")