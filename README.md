# Biyomekanik Sıçrama Analizi

Bu repo, standart kamera görüntüleri üzerinden açık kaynaklı nesne tespiti ve poz tahmini modelleri kullanarak sporcuların sıçrama performanslarını ölçen biyomekanik bir analiz sistemidir. Sistem CMJ, Squat Jump (SJ), Abalakov, Tek Bacak ve Drop Jump testlerini desteklerken, Kütle Merkezi (CoM) takibini uçuş süresi formülleri yerine doğrudan sakrum noktasının yer değiştirmesi üzerinden hesaplayarak "Tuck Effect" yanılgısını ortadan kaldırır.

### Kapsamlı Test Sonuçları (RTX 4050 & i7-13700H | 32 GB RAM)

Aşağıdaki tablo, yapay zeka modellerinin 240/120 FPS manuel Kinovea ölçümlerine kıyasla gösterdiği CoM doğruluk paylarını listelemektedir. 

| Test Tipi | Model Adı | Gerçek CoM | AI CoM | Hata Payı |
| :--- | :--- | :--- | :--- | :--- |
| Video 1 - CMJ | RT-DETR v1 (S) | 44,61 cm | 45 cm | 0,39 cm |
| Video 1 - CMJ | RT-DETRv2 (S) | 44,61 cm | 45,1 cm | 0,49 cm |
| Video 1 - CMJ | RT-DETR (L) | 44,61 cm | 45,5 cm | 0,89 cm |
| Video 1 - CMJ | D-FINE (S) | 44,61 cm | 45,7 cm | 1,09 cm |
| Video 1 - CMJ | MediaPipe | 44,61 cm | 46,1 cm | 1,49 cm |
| Video 1 - CMJ | RT-DETR (L) | 44,61 cm | 46,9 cm | 2,29 cm |
| Video 2 - SJ | RT-DETRv2 (S) | 70,84 cm | 69,5 cm | 1,34 cm |
| Video 2 - SJ | D-FINE (S) | 70,84 cm | 69,3 cm | 1,54 cm |
| Video 2 - SJ | RT-DETR v1 (S) | 70,84 cm | 69,2 cm | 1,64 cm |
| Video 2 - SJ | RT-DETR (L) | 70,84 cm | 69,2 cm | 1,64 cm |
| Video 2 - SJ | RT-DETR (L) | 70,84 cm | 69,2 cm | 1,64 cm |
| Video 2 - SJ | MediaPipe | 70,84 cm | 69 cm | 1,84 cm |
| Video 3 - Abalakov | RT-DETR (L) | 61,76 cm | 60,3 cm | 1,46 cm |
| Video 3 - Abalakov | D-FINE (S) | 61,76 cm | 51 cm | 10,76 cm |
| Video 3 - Abalakov | RT-DETRv2 (S) | 61,76 cm | 50,9 cm | 10,86 cm |
| Video 3 - Abalakov | RT-DETR (L) | 61,76 cm | 50,9 cm | 10,86 cm |
| Video 3 - Abalakov | MediaPipe | 61,76 cm | 50,7 cm | 11,06 cm |
| Video 3 - Abalakov | RT-DETR v1 (S) | 61,76 cm | 50,3 cm | 11,46 cm |
| Video 4 - Drop Jump | RT-DETRv2 (S) | 66,87 cm | 24,5 cm | 42,37 cm |
| Video 4 - Drop Jump | MediaPipe | 66,87 cm | 24,4 cm | 42,47 cm |
| Video 4 - Drop Jump | RT-DETR (L) | 66,87 cm | 24,2 cm | 42,67 cm |
| Video 4 - Drop Jump | RT-DETR v1 (S) | 66,87 cm | 24 cm | 42,87 cm |
| Video 4 - Drop Jump | D-FINE (S) | 66,87 cm | 23,7 cm | 43,17 cm |
| Video 5 - Tek Bacak | RT-DETRv2 (S) | 25,42 cm | 28,3 cm | 2,88 cm |
| Video 5 - Tek Bacak | D-FINE (S) | 25,42 cm | 28,4 cm | 2,98 cm |
| Video 5 - Tek Bacak | RT-DETR v1 (S) | 25,42 cm | 28,5 cm | 3,08 cm |
| Video 5 - Tek Bacak | RT-DETR (L) | 25,42 cm | 28,7 cm | 3,28 cm |
| Video 5 - Tek Bacak | MediaPipe | 25,42 cm | 28,9 cm | 3,48 cm |

**Hız ve Diğer Mühendislik Bulguları**
* **FPS ve İşlem Süresi:** Tüm modeller kare başına ortalama 35,47 ms ile 52,17 ms arasında işlem süresi sergilemiş olup, genel donanım hızı 19,17 FPS ile 28,19 FPS aralığında gerçekleşmiştir.
* **Algoritmik Hata Tespitleri:**
  * **Drop Jump Temas Süresi (GCT):** Başlangıç kutusunun zemin sayılması ve statik beklemenin reaktif sürelere dahil edilmesi sebebiyle, referansı 359 ms olan GCT değerleri AI tarafından ~1900 ms civarında saptanarak 42 cm'lik istikrarlı bir referans sapmasına yol açmıştır.
  * **Abalakov Savrulması:** Kolların serbest kullanımından kaynaklanan bounding box kaymaları, 120 FPS'lik referans çekim haricindeki tüm standart 60 FPS modellerde 10-11 cm aralığında net bir hizalama bozulması yaratmıştır.
