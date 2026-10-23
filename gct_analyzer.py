import cv2

class GCTAnalyzer:
    def __init__(self, fps=60):
        self.fps = fps
        self.is_contact = False
        self.contact_frames = 0
        self.ground_y = 0 
        self.contact_times = []

    def analyze(self, frame, keypoints):
        h, w = frame.shape[:2]
        foot_points = [29, 30, 31, 32]
        valid_foot_y = [keypoints[fp][1] for fp in foot_points if fp in keypoints]

        if valid_foot_y:
            lowest_foot_y = max(valid_foot_y)
            
            if lowest_foot_y > self.ground_y:
                self.ground_y = lowest_foot_y

            # HATA DÜZELTİLDİ: Tolerans 15'ten 40 piksele çıkarıldı
            is_touching = lowest_foot_y >= (self.ground_y - 40)

            if is_touching:
                self.is_contact = True
                self.contact_frames += 1
                cv2.putText(frame, "YERLE TEMAS VAR", (w - 350, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                if self.is_contact and self.contact_frames > 0:
                    gct_ms = (self.contact_frames / self.fps) * 1000
                    self.contact_times.append(gct_ms)
                    self.contact_frames = 0
                self.is_contact = False

            if self.contact_times:
                cv2.putText(frame, f"Son Temas: {self.contact_times[-1]:.1f} ms", (w - 400, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
        return frame