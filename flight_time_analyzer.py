import cv2

class FlightTimeAnalyzer:
    def __init__(self, fps=60):
        self.fps = fps
        self.is_flying = False
        self.flight_frames = 0
        self.ground_y = 0
        self.last_flight_time = 0
        self.last_height_cm = 0

    def analyze(self, frame, keypoints):
        foot_points = [29, 30, 31, 32] 
        valid_foot_y = [keypoints[fp][1] for fp in foot_points if fp in keypoints]

        if valid_foot_y:
            lowest_foot_y = max(valid_foot_y)
            
            if lowest_foot_y > self.ground_y:
                self.ground_y = lowest_foot_y

            # HATA DÜZELTİLDİ: Tolerans 15'ten 40 piksele çıkarıldı
            is_touching = lowest_foot_y >= (self.ground_y - 40)

            if not is_touching:
                self.is_flying = True
                self.flight_frames += 1
                cv2.putText(frame, "HAVADA", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            else:
                if self.is_flying and self.flight_frames > 5: 
                    t_seconds = self.flight_frames / self.fps
                    self.last_flight_time = t_seconds
                    self.last_height_cm = ((9.81 * (t_seconds ** 2)) / 8) * 100
                    self.flight_frames = 0
                self.is_flying = False

            if self.last_height_cm > 0:
                cv2.putText(frame, f"Ucus Suresi: {self.last_flight_time:.2f} s", (50, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 105, 180), 2)
                cv2.putText(frame, f"FT Yukseklik: {self.last_height_cm:.1f} cm", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 105, 180), 2)
                
        return frame