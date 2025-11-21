import os
from src.data_prep import events_to_matrix, summarize_matrix, save_info
from src.sequential import sequential_best_row
from src.dac import dac_best_row
from src.plots_basic import save_heatmap, save_bar_chart

def main():
    # Dosya yollarını dinamik yap (Hata almamak için)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(base_dir, "data","dock_events_raw_sample.csv")
    output_heatmap = os.path.join(base_dir, "plots", "heatmap.png")
    output_barchart = os.path.join(base_dir, "plots", "bar_chart.png")
    output_info = os.path.join(base_dir, "data", "info.json")
    
    delta_mins = 5
    
    if not os.path.exists(input_csv):
        print(f"HATA: '{input_csv}' dosyası bulunamadı!")
        print(f"Lütfen dosyayı şuraya koyun: {base_dir}")
        return

    print("1. Veri hazırlanıyor (Matris oluşturuluyor)...")
    U, docks, slots = events_to_matrix(input_csv, delta_mins)
    
    # Matris Özeti
    summary = summarize_matrix(U)
    print(f"   -> Matris Boyutu: {summary['R']} Satır x {summary['T']} Sütun")
    print(f"   -> Toplam Dolu Hücre: {summary['ones']}")
    print(f"   -> Seyreklik (Sparsity): %{summary['sparsity']*100:.2f}")

    print("\n2. Sequential Algoritma çalışıyor...")
    best_idx, max_count = sequential_best_row(U)
    
    if docks:
        best_dock_name = docks[best_idx]
        print(f"   -> SONUÇ: En yoğun iskele: {best_dock_name} (ID: {best_idx})")
    else:
        print(f"   -> SONUÇ: En yoğun iskele ID: {best_idx}")
        
    print(f"   -> Toplam {max_count} slot boyunca dolu kaldı.")

    print("\n3. Divide-and-Conquer Algoritma çalışıyor...")
    best_idx_dac, max_count_dac = dac_best_row(U)
    
    if docks:
        best_dock_name_dac = docks[best_idx_dac]
        print(f"   -> SONUÇ: En yoğun iskele: {best_dock_name_dac} (ID: {best_idx_dac})")
    else:
        print(f"   -> SONUÇ: En yoğun iskele ID: {best_idx_dac}")
        
    print(f"   -> Toplam {max_count_dac} slot boyunca dolu kaldı.")
    
    # Sonuçların eşleştiğini doğrula
    if best_idx == best_idx_dac and max_count == max_count_dac:
        print("\n   ✓ Her iki algoritma da aynı sonucu verdi!")
    else:
        print("\n   ✗ UYARI: Algoritmalar farklı sonuçlar verdi!")

    print("\n4. Meta bilgisi kaydediliyor...")
    save_info(U, delta_mins, output_info)

    print("\n5. Grafikler çiziliyor...")
    save_heatmap(U, output_heatmap)
    # Docks listesini etiket olarak gönderiyoruz
    save_bar_chart(U, output_barchart, best_dock_idx=best_idx, dock_labels=docks)
    print("   -> Grafikler 'plots/' klasörüne kaydedildi.")
    
    print("\n--- İŞLEM TAMAMLANDI ---")

if __name__ == "__main__":
    main()