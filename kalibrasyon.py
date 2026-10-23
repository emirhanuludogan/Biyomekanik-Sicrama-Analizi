import cv2

points = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append(y) # Sadece dikey (Y) koordinatı kaydediyoruz
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Kalibrasyon", img)
        print(f"{len(points)}. Nokta Secildi - Y Koordinati: {y}")
        
        if len(points) == 2:
            pixel_farki = abs(points[0] - points[1])
            if pixel_farki == 0:
                print("Ayni noktaya tikladiniz, lutfen kodu yeniden baslatin.")
                return
                
            carpan = 50.0 / pixel_farki 
            
            print("\n" + "="*45)
            print(f"📐 KALİBRASYON SONUCU")
            print("="*45)
            print(f"İki çizgi arası piksel farkı : {pixel_farki} px")
            print(f"Gerçek uzunluk referansı     : 50 cm")
            print(f"1 Pikselin CM karşılığı      : {carpan:.5f} cm")
            print("="*45)
            print(f"Lütfen com_analyzer.py dosyanızdaki 'cm_carpani' degerini {carpan:.5f} olarak guncelleyin.")

video_path = '60 fps 1 .mov' 
cap = cv2.VideoCapture(video_path)
ret, img = cap.read()
cap.release()

if ret:
    print("Video ilk karesi acildi.")
    print("Lutfen farenizle once 50cm'lik araligin UST cizgisine, sonra ALT cizgisine TIKLAYIN.")
    
    # --- YENİ EKRAN GÖSTERİMİ (BÜYÜTÜLMÜŞ AMA ORİJİNAL PİKSEL KORUNAN) ---
    cv2.namedWindow("Kalibrasyon", cv2.WINDOW_NORMAL) # Pencerenin boyutlandırılabilir olmasını sağlar
    
    # Bilgisayar ekranının boyutlarına göre tam ekran veya çok büyük açar
    cv2.resizeWindow("Kalibrasyon", 1200, 900) # Kendine göre bu rakamları büyütebilirsin
    
    cv2.imshow("Kalibrasyon", img)
    cv2.setMouseCallback("Kalibrasyon", click_event)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print(f"Hata: '{video_path}' okunamadi. Dosya adinin dogru oldugundan emin olun.")