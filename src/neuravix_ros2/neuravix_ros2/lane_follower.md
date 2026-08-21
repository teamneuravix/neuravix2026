# `lane_follower_node.py` — şerit takibi

> ⚠️ **2026-08-19: bu dosyanın bir kısmı GÜNCEL DEĞİL.** Şerit düğümü o gün
> arkadaşın sürümüyle değiştirildi (bkz. CLAUDE.md'nin son bölümü). Değişen
> ve buradaki anlatımı geçersiz kılan noktalar: morfoloji OPEN artık 3x3,
> fit derecesi 2, ileri bakış `lookahead_frac=0.65` (0.90 değil), fit
> penceresi `fit_far_frac=0.45`, ağırlık üssü 1 (4 değil), eğim sınırı 3.0
> (1.0 değil), `np.std(xs)<5` reddi kaldırıldı, PID `Kp=0.03` (0.08 değil),
> model `serit_v2.pt` (2 sınıf, `lane` süzgeci). **Hâlâ geçerli olan:**
> `/master` ID-2 sözleşmesi, `err_offset` kalibrasyon yordamı, `lane_width_m`
> yalnızca gösterim, `src_pts` kameraya özeldir. Gerekçelerin tamamı ve
> ölçülen sayılar için CLAUDE.md.

Kamera görüntüsünden şerit çizgilerini bulup `/master` üzerinden ID-2
(`"2,<steer>"`) yayınlar. `steer` 15..75 aralığında, **45 = düz**.

Bu dosya, koda sığmayan gerekçeleri ve kalibrasyon yordamlarını tutar.
Koddaki yorumlar kısa tutulmuştur; ayrıntı için buraya bakın.

---

## Boru hattı

```
kamera → 640x360 resize → YOLO segmentasyon (yalnızca 'lane' sınıfı)
  → maskeleri birleştir → morfoloji (CLOSE 11x11 x2, OPEN 3x3 x1)
  → ufuk üstünü sil (y < 0.40*h) → BEV warp (src_pts → dst_pts)
  → sol/sağ bölgeye ayır (mid ∓ 70) → her bölgeye ağırlıklı polinom fit
  (derece 2, yetersiz veride 1) → şerit merkezi (+ eğimden yön önizleme)
  → güven ağırlığı (fit_confidence_px) → PID → steer
```

Fit `y_eval = lookahead_frac*h` (varsayılan 0.65 ≈ 4.8 m) satırında
değerlendirilir. Sol/sağ bölge ayrımında
`mid ± 70` piksellik bir **ölü bant** vardır; oraya düşen çizgi hiçbir bölgeye
girmez.

---

## BEV homografisi (`src_pts`)

Trapez **kameraya özeldir**. Gerçek aracın ZED'i ile CARLA'nın `rgb_front`'u
farklı FOV / yükseklik / pitch'e sahip olduğundan aynı trapez ikisinde birden
doğru olamaz. Bu yüzden `src_pts` bir ROS parametresidir; **varsayılan gerçek
araç değeridir** ve değiştirilmemelidir.

Sıra: `bottom-left, bottom-right, top-right, top-left`.

### Gerçek araç (varsayılan)

```
[170, 357], [639, 358], [367, 210], [312, 210]
```

2026-07-19'da gerçek ZED karesinden kalibre edildi (`pist_18_3tem` bag'i,
`srcpts_click.py` ile tıklanarak).

### CARLA (parametreyle verilir)

Kamera: 640x360, `fov=110`, `z=1.0 m`, `pitch=-5°`.
Trapez tıklamayla değil, kamera iç/dış parametrelerinden **analitik**
hesaplanır. Üretici: `~/Desktop/carla-slalom/bev_kalibre.py`.

Araçta doğrulanmış değer (2026-08-14, yakın kenar 3.5 m / uzak kenar 8 m):

```bash
ros2 run neuravix_ros2 lane_follower --ros-args \
  -p lane_width_m:=3.5 \
  -p src_pts:="[72.1,302.6, 567.9,302.6, 384.7,197.5, 255.3,197.5]"
```

Kamerayı değiştirirsen (`objects.json`'da z / pitch / fov / çözünürlük)
trapez de değişir — `bev_kalibre.py`'yi tekrar çalıştır.

### Doğruluk ölçütü

**Mutlak BEV genişliği değil, tutarlılığı.** Doğru bir IPM paralel şerit
çizgilerini BEV'de dikey ve paralel yapar; yani ölçülen `LaneW`:

- mesafeyle değişmemeli,
- kareden kareye oynamamalı.

`LaneW`'in `dst_pts`'ten türeyen teorik 384 px'e eşit çıkması **şart değildir**,
çünkü tek şerit görülen karelerde `_half_lane()` ölçülen `lane_w_px`'i kullanır;
teorik 192 px yalnızca ilk ölçüm gelene kadar geçerlidir.

CARLA'da ölçülen (araç gözle şerit ortasındayken):

| trapez | LaneW | Error | Steering |
|---|---|---|---|
| gerçek araç ZED trapezi | 415..502, oynak | −46..−64 px | 48–50 (sürekli sola kırma) |
| analitik CARLA trapezi | 274..294 (±10) | −2..+1 px | 44–45 (düz) |

### Uzak kenar neden 8 m

Ufuk satırı 160.4. İlk denenen 12 m'lik trapezin üst kenarı 182.8'e, yani
ufkun **22 piksel** altına düşüyordu. Orada perspektif dejenere: birkaç
piksellik hata metrelerce mesafe hatasına dönüşür, fit uçları "havada" uçuşur
ve BEV o ince şeridi çıktının yarısına gerer. 8 m ile üst kenar 197.5 olur
(ufka 37 px).

| `--far` | üst kenar | ufka uzaklık |
|---|---|---|
| 12 m | 182.8 | 22 px |
| 10 m | 188.3 | 28 px |
| **8 m** | **197.5** | **37 px** |
| 7 m | 204.8 | 44 px |

Dördü de geçerli IPM; fark yalnızca dayanıklılıkta. Daha uzun ileri görüş
istenirse 10 m ara seçenektir.

---

## Yarım şerit genişliği (`_half_lane`)

Yalnızca **tek** şerit fit edilebildiğinde merkez `fit ± half_lane` ile tahmin
edilir. Bu tahminin hatası doğrudan direksiyona biner, o yüzden değeri önemli:

- `lane_w_px` ölçülmüşse onun yarısı kullanılır (`half_lane_min..max` arasına
  clamp: 96..256 px),
- ölçüm yoksa teorik `0.30 * img_w = 192 px`.

Geçmiş: eskiden `img_w // 4 = 160` kullanılıyordu → tek-şerit karelerde 32 px
merkez biası → integral doyup direksiyonu mıhlıyordu. 2026-07-20 araç kaydında
gerçek `LaneW` ~300 px ölçüldü (yarısı ~150), teorik 192 kullanmak merkezi
~42 px yanlış tarafa kaydırıyordu — sağ çizgi görülüyorken merkez sola kayıyor,
araç sürekli sola kırıyordu. Bu yüzden ölçülen değer önceliklidir.

---

## PID ve anti-windup

`Kp=0.08, Ki=0.001, Kd=0.01`. Üç ayrı koruma var, üçü de gerçek arıza sonrası
eklendi:

1. **`i_term_max = 10.0`** — `Ki*integral` teriminin mutlak üst sınırı (derece).
   2026-07-12 araç testi: sınırsız integral, sabit küçük hatayla dakikalar
   içinde direksiyonu 15/75 uçlarına mıhladı; hata işaret değiştirince yavaşça
   öbür uca sürükledi.

2. **`i_leak = 0.98`** — her tik `integral *= i_leak`. `Ki` çok küçük olduğu
   için integral ~10000'e birikip clamp'te **mıhlanıyor**, küçük hatayla 500+
   karede boşalıyordu (2026-07-19 bag: Error küçükken bile steering 36/33).
   Sızıntı clamp'te sonsuza takılmayı önler, birikmiş bias birkaç saniyede
   çözülür.

3. **Koşullu integrasyon** — integral yalnızca *bu karede iki şerit de
   bulunduysa* **ve** `|err| <= i_error_band` (40 px) iken birikir. Sistematik
   bias (tek-şerit tahmini veya çarpık BEV) varken integral clamp'e dayanıp
   çıkışı mıhlıyordu (45 sn boyunca sabit steer=27). `allow_integral=False`
   iken integral dondurulur: ne birikir ne boşalır.

`reset()` şerit kaybında çağrılır; bayat integral yeni şerit bulununca yanlış
yöne çektirmesin diye.

---

## Şerit kaybı (`lane_lost_frames`, varsayılan 15)

Model üst üste bu kadar karede **hiç maske** bulamazsa bayat `left_prev` /
`right_prev` fitleri ve PID sıfırlanır, `lane_x` merkezde kalır, `err = 0`
zorlanır ve `/master`'a nötr 45 gider (FSM düz devam eder).

2026-07-12 araç testi: kapalı alanda model 53.000+ kare boyunca 0 maske buldu,
ama düğüm tek bir yanlış tespitin bayat fitiyle + PID windup'ıyla sürekli 15/75
uçlarında açı yayınlıyordu.

`lane_lost` iken `err` sıfıra **zorlanır**; böylece `err_offset` nötr 45'i
bozmaz.

> **Dikkat:** sayaç yalnızca *maske yokken* artar. Maske var ama fitlerin hepsi
> reddediliyorsa `lane_lost` tetiklenmez ve bayat fitler kullanılmaya devam
> eder. Bilinen açık nokta.

---

## `err_offset` — sıfır noktası kalibrasyonu

`src_pts` ve kameranın yanal montaj ofseti nedeniyle araç fiziksel olarak
şeridin ortasındayken bile `err != 0` okunabilir.

Yordam:

1. Düz bir bölümde sürücü aracı gözle şerit ortasında tutar.
2. Overlay'deki **`AvgErr`** okunur (3 sn'lik kayan ortalama; yeşil referans
   çizgisi aracın tam ortadayken sarı merkez çizgisinin oturması gereken yeri
   gösterir — sarı-yeşil açıklığı anlık hatadır).
3. Düğüm `-p err_offset:=<mevcut + AvgErr>` ile yeniden başlatılır.

Parametre **yalnızca başlangıçta** okunur; `ros2 param set` işe yaramaz, her
deneme için yeniden başlatmak gerekir.

---

## `lane_width_m` — sadece görüntüleme

`err_m = err_px * lane_width_m / lane_w_px`. PID **ham piksel hatasıyla**
beslenir; bu parametre yalnızca overlay'deki `Error: Npx (+X.XXm)` yazısını
üretir.

- Varsayılan **3.0** — gerçek pistte iki beyaz çizgi arası ölçüldü (2026-07-20):
  yer yer değişken, çoğu yerde ~2.96 m.
- CARLA şeritleri **3.5 m** (haritadan doğrulandı) → sim'de `-p lane_width_m:=3.5`.

Pist genişliği gerçekten değişken olduğu için `err_offset` **piksel** cinsinden
kalibre edilmelidir, metre okumasına göre değil.

---

## Model ve güven eşiği

`model_file` (varsayılan `best_yolo11.pt`) ve `yolo_conf` (varsayılan 0.25,
ultralytics'in kendi eşiği) parametredir. Modeller
`share/neuravix_ros2/models/` altındadır; olmayan bir dosya verilirse hata
basılıp varsayılana dönülür.

Gerekçe: CARLA'da model çoğu karede yalnızca **tek** şerit çizgisi buluyor.
Tek fit olunca merkez tahmin edilir ve hatası doğrudan direksiyona biner.
İkinci çizgiyi yakalamak için eşiği düşürmek (`-p yolo_conf:=0.10`) veya başka
bir model denemek (`-p model_file:=best_250.pt`) gerekiyordu; bunların her
denemesi için kod değiştirip yeniden derlemek gereksizdi.

**Not:** CARLA'da bazı kesitlerde hiç maske çıkmaması normaldir — o yollarda
gerçekten şerit çizgisi yoktur (kavşaklar, geniş açık alanlar).

---

## Kamera topic'i

`camera_topic` parametreli. **Varsayılan gerçek araçtır**
(`/zed/zed_node/rgb/image_rect_color` — 2026-07-12'de araçta ~28 Hz
doğrulandı); simülasyonda CARLA kamerası parametreyle geçilir:

```bash
-p camera_topic:=/carla/ego_vehicle/rgb_front/image
```

Bu, `src_pts` ve `obstacle_lidar`'ın `lidar_topic`'i ile aynı desendir:
varsayılanlar araca göre, sim farkları çağrı yerinde. Parametre unutulursa
düğüm sessizce yanlış veri üretmez — hiç görüntü gelmez ve `lane_lost` devreye
girip nötr 45 yayınlar. Açılış log'u hangi topic'e abone olunduğunu yazar.

2026-08-13'te `rgb_overlay` yerine **ham** kameraya geçildi: `tabela_overlay`
düğümüne bağımlılık kalktı, slalom test kurulumunda bir düğüm azaldı.

Abonelik `qos_profile_sensor_data` (**best-effort**) ile yapılır: ZED gibi
gerçek kamera sürücüleri best-effort yayınlayabilir ve reliable bir abonelik
onlarla **hiç eşleşmez** (hata da vermez, sadece veri gelmez). Best-effort
abonelik CARLA'nın reliable yayınıyla da uyumludur.

---

## Hata ayıklama çıktısı

- **Topic:** overlay JPEG olarak `/neuravix/lane_debug/compressed`
  (`publish_debug_image`, varsayılan açık). Gerçek araçta container'ın
  `DISPLAY`'i yoktur; laptoptan `rqt_image_view` ile ya da
  `ros2 run neuravix_ros2 mjpeg_server` ile tarayıcıdan izlenir.
- **Pencere:** `cv2.imshow` (`show_window`, varsayılan açık). `DISPLAY` boşsa
  otomatik kapatılır (imshow çökmesini önlemek için).
- **Video kaydı:** pencere odaktayken **`r`** tuşu kaydı başlatır/durdurur;
  dosya `~/neuravix_kayit/serit_takip_<zaman>.mp4`.

---

## Parametreler

| parametre | varsayılan | açıklama |
|---|---|---|
| `camera_topic` | `/zed/zed_node/rgb/image_rect_color` | giriş görüntüsü; **CARLA'da parametreyle geçilir** |
| `src_pts` | ZED trapezi (8 sayı) | BEV kaynak trapezi; 8 sayı değilse hata + varsayılan |
| `model_file` | `best_yolo11.pt` | `models/` altındaki YOLO dosyası |
| `yolo_conf` | 0.25 | YOLO güven eşiği |
| `lane_lost_frames` | 15 | kaç maskesiz kareden sonra nötr 45 |
| `i_error_band` | 40.0 | integralin birikebileceği hata bandı (px) |
| `err_offset` | 0.0 | sıfır noktası kalibrasyonu (px) |
| `lane_width_m` | 3.0 | **yalnız görüntüleme**; CARLA'da 3.5 |
| `publish_debug_image` | true | overlay JPEG topic'i |
| `show_window` | true | `cv2.imshow` penceresi |

Hepsi **başlangıçta** okunur — `ros2 param set` etkisizdir.

---

## Bilinen açık noktalar

- Maske var ama fitler reddediliyorsa `lane_lost` tetiklenmez; bayat fitler
  süresiz kullanılabilir.
- Çok şeritli yolda sol/sağ fitler ego şeridinin sınırları yerine yolun dış
  sınırlarını yakalayabilir; `LaneW` o kesitlerde beklenenden geniş çıkar.
- Model sarı orta çizgiyi de beyaz kesikli çizgiyi de aynı `lane` sınıfına
  koyar; hangi çizginin yakalandığı bölgeye göre değişir.
