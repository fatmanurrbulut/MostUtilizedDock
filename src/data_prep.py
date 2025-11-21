import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def build_time_grid(day_start, day_end, delta_minutes):
    """
    Başlangıç ve bitiş saati arasında zaman dilimleri oluşturur.
    Güncelleme: Pandas freq parametresi 'min' olarak ayarlandı.
    """
    # 'T' yerine 'min' kullanıyoruz (FutureWarning düzeltmesi)
    slots = pd.date_range(start=day_start, end=day_end, freq=f'{delta_minutes}min')
    return slots.to_pydatetime().tolist()

def events_to_matrix(csv_path, delta_minutes=5):
    """
    CSV dosyasını okur ve U (Doluluk) matrisini oluşturur.
    """
    # 1. Veriyi Oku
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    
    df['arrival_time'] = pd.to_datetime(df['arrival_time'])
    df['departure_time'] = pd.to_datetime(df['departure_time'])

    # 2. Zaman Izgarasını Kur
    if len(df) > 0:
        # 'H' yerine 'h' kullanıyoruz (FutureWarning düzeltmesi)
        day_start = df['arrival_time'].min().floor('h') 
        day_end = df['departure_time'].max().ceil('h')
    else:
        now = datetime.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = now.replace(hour=23, minute=59, second=0, microsecond=0)

    slots = build_time_grid(day_start, day_end, delta_minutes)
    
    docks = sorted(df['dock_id'].unique()) if 'dock_id' in df.columns else []
    dock_map = {d: i for i, d in enumerate(docks)} 
    
    R = len(docks)
    T = len(slots)
    
    # 3. Matrisi Doldur
    U = np.zeros((R, T), dtype=int)
    
    for _, row in df.iterrows():
        if row['dock_id'] in dock_map:
            r = dock_map[row['dock_id']]
            t_start = np.searchsorted(slots, row['arrival_time'], side='right') - 1
            t_end = np.searchsorted(slots, row['departure_time'], side='left')
            
            t_start = max(0, t_start)
            t_end = min(T, t_end)
            
            if t_start < t_end:
                U[r, t_start:t_end] = 1 
        
    return U, docks, slots

def summarize_matrix(U):
    """
    Matris istatistiklerini döner.
    """
    R, T = U.shape
    total_ones = int(np.sum(U))
    total_cells = R * T
    sparsity = 1.0 - (total_ones / total_cells) if total_cells > 0 else 0.0
    
    return {
        "R": R,
        "T": T,
        "ones": total_ones,
        "sparsity": sparsity
    }


def save_info(U, delta_minutes, output_path="data/info.json"):
    """
    Matris meta bilgilerini JSON dosyasına kaydeder.
    
    Args:
        U: Occupancy matrix (R×T)
        delta_minutes: Zaman slot uzunluğu (dakika)
        output_path: JSON dosyasının kaydedileceği yol
    
    Returns:
        dict: Kaydedilen meta bilgisi
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    summary = summarize_matrix(U)
    info = {
        "R": summary["R"],
        "T": summary["T"],
        "ones": summary["ones"],
        "sparsity": round(summary["sparsity"], 4),
        "delta": delta_minutes
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print(f"Meta bilgisi kaydedildi: {output_path}")
    return info
