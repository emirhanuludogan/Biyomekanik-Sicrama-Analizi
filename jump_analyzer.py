import cv2
import time
import torch
import sys
import os
import mediapipe as mp
import numpy as np
import torchvision.transforms as T
from report_generator import ReportGenerator
from com_analyzer import CoMAnalyzer
from gct_analyzer import GCTAnalyzer
from flight_time_analyzer import FlightTimeAnalyzer

class ModelRouter:
    """SADECE DETR modellerini (D-FINE, DEIM, RT-DETR) ve MediaPipe Baseline'i yoneten yonlendirici."""
    def __init__(self, model_path, model_type='ultralytics'):
        self.model_type = model_type
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Cihaz: {self.device} | Yuklenen Model: {model_path}")
        
        self.model = None

        if self.model_type == 'ultralytics':
            from ultralytics import RTDETR
            self.model = RTDETR(model_path)
            
        elif self.model_type == 'mediapipe':
            self.mp_pose = mp.solutions.pose
            self.model = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)
            print("[MediaPipe] Baseline sistemi (Sirket Mevcut Urunu) dedektor olarak yuklendi.")
                
        elif self.model_type in ['dfine', 'deim', 'rtdetr_v1', 'rtdetr_v2']:
            if self.model_type == 'dfine':
                repo_path = os.path.abspath('PeterandeD-FINE')
                config_path = os.path.join(repo_path, 'configs/dfine/dfine_hgnetv2_s_coco.yml') 
            elif self.model_type == 'deim':
                repo_path = os.path.abspath('yzd-vDEIM')
                config_path = os.path.join(repo_path, 'configs/deim_dfine/deim_hgnetv2_s_coco.yml')
            elif self.model_type == 'rtdetr_v1':
                repo_path = os.path.abspath('lyuwenyuRT-DETR/rtdetrv2_pytorch')
                # RT-DETR v1 için özel config dosyası:
                config_path = os.path.join(repo_path, 'configs/rtdetr/rtdetr_r18vd_6x_coco.yml')
            elif self.model_type == 'rtdetr_v2': 
                repo_path = os.path.abspath('lyuwenyuRT-DETR/rtdetrv2_pytorch')
                # RT-DETR v2 için özel config dosyası:
                config_path = os.path.join(repo_path, 'configs/rtdetrv2/rtdetrv2_r18vd_120e_coco.yml')

            sys.path.insert(0, repo_path)
            
            try:
                if self.model_type == 'deim':
                    from engine.core import YAMLConfig
                    # Windows libuv hatasını aşmak için çevre değişkenleriyle sahte dağıtık kurulum (Gloo OLMADAN)
                    os.environ["LOCAL_RANK"] = "0"
                    os.environ["RANK"] = "0"
                    os.environ["WORLD_SIZE"] = "1"
                    os.environ["MASTER_ADDR"] = "localhost"
                    os.environ["MASTER_PORT"] = "12345"
                else:
                    from src.core import YAMLConfig
                
                print(f"[{self.model_type.upper()}] Orijinal mimari kuruluyor...")
                
                cfg = YAMLConfig(config_path, resume=model_path)
                checkpoint = torch.load(model_path, map_location=self.device)
                state = checkpoint.get('ema', {}).get('module', checkpoint.get('model'))
                cfg.model.load_state_dict(state)
                
                self.model = cfg.model.eval().to(self.device)
                print(f"[{self.model_type.upper()}] Agirliklar basariyla GPU'ya yuklendi!")
            except Exception as e:
                print(f"[{self.model_type.upper()}] Model yuklenirken hata olustu: {e}")
                self.model = None

    def predict_person(self, frame):
        best_bbox = None
        max_area = 0

        if self.model_type == 'ultralytics':
            results = self.model(frame, classes=[0], verbose=False)
            if results[0].boxes:
                for box in results[0].boxes.xyxy.cpu().numpy():
                    x1, y1, x2, y2 = map(int, box)
                    area = (x2 - x1) * (y2 - y1)
                    if area > max_area:
                        max_area = area
                        best_bbox = [x1, y1, x2, y2]
                        
        elif self.model_type == 'mediapipe':
            h, w = frame.shape[:2]
            results = self.model.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                x_coords = [lm.x for lm in results.pose_landmarks.landmark]
                y_coords = [lm.y for lm in results.pose_landmarks.landmark]
                
                x1 = max(0, int(min(x_coords) * w) - 20)
                y1 = max(0, int(min(y_coords) * h) - 20)
                x2 = min(w, int(max(x_coords) * w) + 20)
                y2 = min(h, int(max(y_coords) * h) + 20)
                
                best_bbox = [x1, y1, x2, y2]
                        
        elif self.model_type in ['dfine', 'deim', 'rtdetr_v1', 'rtdetr_v2']:
            if self.model is None: return None
            
            h, w = frame.shape[:2]
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 640))
            tensor_img = T.ToTensor()(img).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(tensor_img)
            
            if 'pred_boxes' in output:
                boxes = output['pred_boxes'][0]
                logits = output['pred_logits'][0]
                
                scores = torch.nn.functional.softmax(logits, dim=-1)[:, 0] 
                
                if len(scores) > 0 and torch.max(scores) > 0.4:
                    best_idx = torch.argmax(scores)
                    cx, cy, bw, bh = boxes[best_idx].cpu().numpy()
                    
                    x1 = int((cx - bw/2) * w)
                    y1 = int((cy - bh/2) * h)
                    x2 = int((cx + bw/2) * w)
                    y2 = int((cy + bh/2) * h)
                    
                    best_bbox = [max(0, x1), max(0, y1), min(w, x2), min(h, y2)]
            
        return best_bbox

class TopDownJumpAnalyzer:
    def __init__(self, model_path='mediapipe', model_type='mediapipe', test_type='CMJ'):
        self.detector = ModelRouter(model_path, model_type)
        self.test_type = test_type 
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)
        self.frame_count = 0
        
        self.com_analyzer = CoMAnalyzer()
        self.gct_analyzer = GCTAnalyzer(fps=60)
        self.ft_analyzer = FlightTimeAnalyzer(fps=60)
        
        self.total_frames = 0
        self.detected_frames = 0
        self.inference_times = []

    def process_frame(self, frame):
        self.total_frames += 1
        h, w = frame.shape[:2]
        
        start_time = time.time()
        
        bbox = self.detector.predict_person(frame)
        
        if bbox:
            self.detected_frames += 1
            x1, y1, x2, y2 = bbox
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
            
            cropped_person = frame[y1:y2, x1:x2]
            pose_results = self.pose.process(cv2.cvtColor(cropped_person, cv2.COLOR_BGR2RGB))
            
            global_keypoints = {}
            if pose_results.pose_landmarks:
                for idx, landmark in enumerate(pose_results.pose_landmarks.landmark):
                    gx, gy = x1 + int(landmark.x * cropped_person.shape[1]), y1 + int(landmark.y * cropped_person.shape[0])
                    global_keypoints[idx] = (gx, gy)
                    cv2.circle(frame, (gx, gy), 3, (0, 255, 0), -1)

                frame = self.com_analyzer.analyze(frame, self.total_frames, global_keypoints)
                frame = self.ft_analyzer.analyze(frame, global_keypoints)
                
                if self.test_type == 'DROP_JUMP':
                    frame = self.gct_analyzer.analyze(frame, global_keypoints)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        inference_time = time.time() - start_time
        self.inference_times.append(inference_time)
            
        return frame, None

    def print_performance_report(self):
        det_rate = (self.detected_frames / self.total_frames) * 100 if self.total_frames > 0 else 0
        avg_infer_sec = np.mean(self.inference_times) if self.inference_times else 0
        avg_infer_ms = avg_infer_sec * 1000
        avg_fps = 1.0 / avg_infer_sec if avg_infer_sec > 0 else 0
        
        print("\n" + "="*40)
        print("📊 MODEL PERFORMANS RAPORU")
        print("="*40)
        print(f"Secili Test Tipi    : {self.test_type}")
        print(f"Toplam Islenen Kare : {self.total_frames}")
        print(f"Basarili Tespit     : {self.detected_frames}")
        print(f"Tespit Orani        : %{det_rate:.2f}")
        print(f"Kare Basina Sure    : {avg_infer_ms:.2f} ms")
        print(f"Ortalama Hiz (FPS)  : {avg_fps:.2f} FPS")
        print("="*40 + "\n")

        perf_data = {
            'total_frames': self.total_frames,
            'detected_frames': self.detected_frames,
            'det_rate': det_rate,
            'avg_infer_ms': avg_infer_ms,
            'avg_fps': avg_fps
        }
        
        reporter = ReportGenerator("test_sonuclari.txt")
        reporter.save_report(
            com_max=self.com_analyzer.max_sicrama_cm,
            ft_time=self.ft_analyzer.last_flight_time,
            ft_height=self.ft_analyzer.last_height_cm,
            gct_times=self.gct_analyzer.contact_times,
            perf_data=perf_data
        )

if __name__ == "__main__":
    print("\n" + "="*40)
    print("🏃 ZIPLAMA TESTİ SEÇİM EKRANI")
    print("="*40)
    print("1 - CMJ (Eller belde, hızlı sıçrama)")
    print("2 - SJ (Squat Jump - 90 derecede bekleme)")
    print("3 - ABALAKOV (Kollar serbest)")
    print("4 - TEK BACAK CMJ")
    print("5 - DROP JUMP (Kutudan atlama - Temas Süresi ölçer)")
    print("="*40)
    
    secim = input("Lütfen yapacağınız testi seçin (1-5): ")
    
    test_tipleri = {
        '1': 'CMJ',
        '2': 'SJ',
        '3': 'ABALAKOV',
        '4': 'TEK_BACAK',
        '5': 'DROP_JUMP'
    }
    
    secili_test = test_tipleri.get(secim.strip(), 'CMJ')
    
    print(f"\n✅ Seçilen Test Tipi: {secili_test}")
    print("Yapay Zeka Analizi Başlıyor...\n")

    # Modeli buradan değiştiriyorsun
    analyzer = TopDownJumpAnalyzer('rtdetr_r18vd_dec3_6x_coco_from_paddle.pth', 'rtdetr_v1', test_type=secili_test)
    
    # Doğru Abalakov video dosyanın adını buraya yazıyorsun
    cap = cv2.VideoCapture('sj.mov')
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        processed_frame, keypoints = analyzer.process_frame(frame)
        
        h_orig, w_orig = processed_frame.shape[:2]
        hedef_yukseklik = 700 
        yeni_genislik = int(w_orig * (hedef_yukseklik / h_orig))
        cv2.imshow('Jump Analysis', cv2.resize(processed_frame, (yeni_genislik, hedef_yukseklik)))
        
        if cv2.waitKey(15) & 0xFF == ord('q'): break
            
    cap.release()
    cv2.destroyAllWindows()
    analyzer.print_performance_report()