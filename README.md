# Biyomekanik Sıçrama Analizi

Bu repo, açık kaynaklı nesne tespiti (RT-DETR serisi, D-FINE) ve poz tahmini (MediaPipe) modelleriyle sporcuların sıçrama performanslarını (CMJ, Squat Jump, Abalakov, Tek Bacak, Drop Jump) standart kamera görüntüleri üzerinden analiz eden bir sistemdir[cite: 2].

**Temel Analiz Yöntemi**
* **Kütle Merkezi (CoM):** Sıçrama yüksekliği, uçuş süresi yerine doğrudan sakrum (kalça) noktasının dikey yer değiştirmesi üzerinden hesaplanarak sporcunun havadayken dizlerini bükmesiyle manipüle edilebilen "Tuck Effect" yanılgısı önlenmiştir[cite: 2].
* **Temas Süresi (GCT):** Drop Jump testlerinde reaktif gücü ölçmek için topuk ve ayak başparmağı noktaları izlenir[cite: 2].

**Örnek Test Sonuçları**
NVIDIA GeForce RTX 4050 Laptop GPU & i7-13700H (32 GB RAM) donanımıyla elde edilen 60 FPS ölçüm kıyaslamalarının bir özeti aşağıdadır[cite: 1, 2]:

| Test Tipi | Model Adı | Gerçek CoM | AI CoM | Hata Payı |
| :--- | :--- | :--- | :--- | :--- |
| CMJ | RT-DETR v1 (S) | 44,61 cm | 45,0 cm | 0,39 cm |
| SJ | D-FINE (S) | 70,84 cm | 69,3 cm | 1,54 cm |
| Abalakov | RT-DETR (L) | 61,76 cm | 60,3 cm | 1,46 cm |
| Drop Jump | MediaPipe | 66,87 cm | 24,4 cm | 42,47 cm |
| Tek Bacak | RT-DETRv2 (S) | 25,42 cm | 28,3 cm | 2,88 cm |

Tablo Notu: Abalakov testinde kolların serbest savrulması bounding box hizalamasını zorlarken, Drop Jump testinde yüksekte başlama durumu algoritmik zemin referansı kaymalarına (kutuyu zemin sanma) neden olabilmektedir.
