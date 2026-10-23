import cv2
import numpy as np

class CoMAnalyzer:
    def __init__(self):
        self.reference_y_list = []
        self.sanal_referans_y = None
        # DEĞİŞİKLİK 1: Artık piksel (px) değil, santimetre (cm) tutuyoruz
        self.max_sicrama_cm = 0 

    def analyze(self, frame, frame_count, keypoints):
        h, w = frame.shape[:2]
        # 23: Sol Kalça, 24: Sağ Kalça
        if 23 in keypoints and 24 in keypoints:
            com_x = int((keypoints[23][0] + keypoints[24][0]) / 2)
            com_y = int((keypoints[23][1] + keypoints[24][1]) / 2)
            cv2.circle(frame, (com_x, com_y), 8, (0, 0, 255), -1)
            
            if frame_count <= 15:
                self.reference_y_list.append(com_y)
                cv2.putText(frame, "Kalibrasyon...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            elif self.sanal_referans_y is None:
                self.sanal_referans_y = np.mean(self.reference_y_list)
                
            if self.sanal_referans_y is not None:
                anlik_yukseklik_px = self.sanal_referans_y - com_y
                
                # --- DEĞİŞİKLİK 2: SANTİMETRE ÇEVİRİSİ ---
                cm_carpani = 0.19230 # Hesapladığımız ortalama kalibrasyon çarpanı
                anlik_yukseklik_cm = max(0, anlik_yukseklik_px * cm_carpani)
                
                # Maksimum yüksekliği cm olarak güncelliyoruz
                self.max_sicrama_cm = max(self.max_sicrama_cm, anlik_yukseklik_cm)
                # ------------------------------------------

                ref_y_int = int(self.sanal_referans_y)
                cv2.line(frame, (0, ref_y_int), (w, ref_y_int), (0, 255, 255), 2)
                
                # DEĞİŞİKLİK 3: Ekrana px yerine cm yazdırıyoruz (.1f ile virgülden sonra 1 basamak gösteriyoruz)
                cv2.putText(frame, f"Yukseklik: {anlik_yukseklik_cm:.1f} cm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                cv2.putText(frame, f"Max: {self.max_sicrama_cm:.1f} cm", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
        return frame