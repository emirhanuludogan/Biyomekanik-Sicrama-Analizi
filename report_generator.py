import os

class ReportGenerator:
    """Test sonuçlarını ve model performansını .txt dosyasına kaydeden modül."""
    def __init__(self, filename="test_sonuclari.txt"):
        self.filename = filename

    def save_report(self, com_max, ft_time, ft_height, gct_times, perf_data):
        # 'w' (write) modu ile açıyoruz: Bu sayede her yeni testte dosya SIFIRLANIR ve eskinin üzerine yazar.
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write("="*45 + "\n")
            f.write("🏃 ZIPLAMA TESTİ ANALİZ SONUÇLARI\n")
            f.write("="*45 + "\n\n")
            
            f.write("📍 BİYOMEKANİK VERİLER:\n")
            f.write(f"- Maksimum Sıçrama (CoM) : {com_max:.1f} cm\n")
            
            if ft_time > 0:
                f.write(f"- Havada Kalma Süresi    : {ft_time:.2f} saniye\n")
                f.write(f"- Uçuş Süresi Yüksekliği : {ft_height:.1f} cm\n")
            else:
                f.write("- Havada Kalma Süresi    : Tespit edilmedi\n")
                
            if gct_times:
                # Sadece yapılan en son temas süresini (GCT) yazar
                f.write(f"- Yerle Temas Süresi     : {gct_times[-1]:.1f} ms\n")
            else:
                f.write("- Yerle Temas Süresi     : Tespit edilmedi\n")

            f.write("\n" + "="*45 + "\n")
            f.write("📊 MODEL PERFORMANS RAPORU\n")
            f.write("="*45 + "\n")
            f.write(f"- Toplam İşlenen Kare    : {perf_data['total_frames']}\n")
            f.write(f"- Başarılı Tespit Oranı  : %{perf_data['det_rate']:.2f}\n")
            f.write(f"- Kare Başına İşlem Süresi: {perf_data['avg_infer_ms']:.2f} ms\n")
            f.write(f"- Ortalama Hız (FPS)     : {perf_data['avg_fps']:.2f} FPS\n")
            f.write("="*45 + "\n")
        
        print(f"\n[BİLGİ] Sonuclar basariyla '{self.filename}' dosyasina kaydedildi!")