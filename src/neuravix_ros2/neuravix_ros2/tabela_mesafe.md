# Tabela mesafesi: ZED derinliği (25.08.2026)

`tabela_tespit_node.py` → `/master` ID-3 → `decision_brain.py` zincirindeki
**mesafe** alanının nasıl üretildiği. Bu dosya değişikliğin *nedenini* tutar;
parametrelerin güncel değerleri her zaman koddadır.

## Önceki durum ve neden bıraktık

Mesafe tek başına 2B bounding-box yüksekliğinden türetiliyordu:

```
d = sabit / h        sabit = odak_uzaklığı × nesnenin GERÇEK yüksekliği
```

Bu formülün kendisi doğrudur; sorun `sabit`in **nesnenin fiziksel boyutunu
bilmeyi şart koşması**. Bilmiyorduk. Sabit simülasyondaki tabelaya göre
kurulmuştu (`camera_overlay_node.py` içinde `SIGN_REAL_W = 0.9`), gerçek
pistteki tabela ise başka boyutta.

Yan etkiler:

- Sabit **nesne türüne** bağlı olduğu için tek modelde hem tabela hem ışık
  olunca tek sabit yetmedi; 18.08.2026'da ışıklara ayrı bir sabit (150)
  eklendi. Bu, aynı eşiğin tetiklendiği gerçek mesafeyi **tam 3 kat**
  değiştirdi — saf aritmetik, ölçümden bağımsız.
- Sabit **kameraya** da bağlı: CARLA `rgb_front` ile ZED2'nin odak uzaklığı
  aynı değil, çözünürlük değişince de ölçek kayıyor.
- Kutunun ne kadar sıkı çizildiği (kırpılma, kısmi görünürlük) doğrudan
  mesafeye karışıyor.

## Ölçüm: hareketten ölçek

`joystick_46` bag'i üzerinde (gerçek araç, ZED 1280×720, 290 s) ölçüldü.
`d = K/h` ve `d(t) = d₀ − s(t)` olduğundan

```
s(t) = d₀ − K · (1/h(t))
```

`s(t)` araç hızından integre edilen yol. `(1/h, s)` doğrusal regresyonunun
eğimi doğrudan `K` verir ve bu **odak uzaklığından da nesne boyutundan da
bağımsızdır**.

| nesne | tespit | ölçülen K | o günkü sabit | kod / gerçek |
|---|---|---|---|---|
| `DUR_TT-2` | 519 kare, h 22→40 px | **362** | 450 | 1.24× (fazla) |
| `Yesil_Isik` | 531 kare, h 10→22 px | **218** | 150 | 0.69× (eksik) |

Regresyon RMS'i sırasıyla 0.33 m ve 1.49 m.

İki nesne **ters yönlerde** sapıyor: tek bir düzeltme çarpanı ikisini birden
düzeltemez. Ekibin araç üzerinde deneme-yanılmayla bulduğu "kodda 4 m
ayarlayınca gerçekte 2 m" gözlemi, ışıklara da 450 uygulanan döneme denk
gelir: 450 / 218 = **2.06**.

**Doğruluk sınırı:** CAN hızı `uint8 km/h` ve kayıtta yalnız 0–3 km/h var.
Bu, K'ların **mutlak** değerine ~%30 belirsizlik katar; ikisinin **oranı**
aynı hız kaynağını paylaştıkları için sağlamdır. Derinlik akarken bu
sabitler zaten kullanılmıyor.

## Şimdiki mimari

```
ZED sol rektifiye RGB ──► YOLO ──► bbox
                                    │
ZED depth_registered ──► son kare ──┴─► iç ROI medyanı ──► metre
                          (zaman damgası kontrolü)          │
                                                            ▼
                              /master  "3,<id>,<metre>,<cx>,<cy>,<w>,<h>,<src>"
```

- **Mesafe artık gerçek metre** ve **ön tampon referanslı** — ID-4 engel
  mesafeleriyle aynı referans, dolayısıyla beyindeki eşikler iki kaynak için
  de aynı şeyi ifade ediyor.
- **8. alan `<src>`**: `1` = ZED derinliğinden ölçüldü, `0` = bbox tahmini.
  Sona eklendi, eski tüketiciler etkilenmez; göndermeyeni beyin tahmin sayar.

### Neden `message_filters` değil

Derinlik ayrı abone edilip **son kare saklanıyor**, RGB karesiyle zaman
damgası farkı `depth_max_age` ile kontrol ediliyor. Senkron abonelik
kullanılsaydı derinlik hiç gelmediğinde senkronizer RGB'yi de bloklardı ve
tabela tespiti tamamen susardı. 2026-07-11'de araçta ZED wrapper ayaktaydı,
topic'i reklam ediyordu ve tek kare akmıyordu — bu senaryo teorik değil.

### Eşleştirme: en yakın kare, en yenisi değil

Son **N** derinlik karesi bir halka tamponda tutulur ve RGB'nin zaman
damgasına **en yakın** olan seçilir. Tek kare saklamak yetmiyor: YOLO çıkarımı
~160 ms sürdüğü için işlenen RGB karesi kuyrukta geride kalır, elde tutulan
derinlik ise ondan daha yenidir. O zaman (a) yaş eşiği aşılır ve gereksiz yere
tahmine düşülür, (b) daha kötüsü, eşleştirilseydi bbox eski karedeki konumu
gösterirken derinlik yeni kareden okunurdu — araç ilerlemiş, tabela ekranda
kaymış, **yanlış pikseller** örneklenmiş olurdu.

Bu, duman testinde yakalandı: düzeltmeden önce tespitlerin önemli kısmı
"derinlik bayat" deyip tahmine düşüyordu.

### Bant genişliği — ölçülmesi gereken şey

720p `32FC1` bir derinlik karesi **3.7 MB**. 28 Hz'de ~103 MB/s. Best-effort
UDP'de böyle bir mesaj ~57 parçaya bölünür ve **tek parçanın kaybı mesajın
tamamını düşürür**. Masaüstü duman testinde yayıncı 10 Hz basarken düğüme
yalnızca **2.9–4.6 Hz** ulaştı; ölçüm oranı %79'da kaldı. Araçta Fast DDS
paylaşımlı bellek (`--ipc=host`) bunu ciddi biçimde iyileştirir ama
**varsayılmamalı, ölçülmeli**.

Düğüm bunu kendi kendine raporluyor — 15 saniyede bir:

```
[derinlik] 201 kare (~4.6 Hz) | olculen 141/201 (%70)
```

Kaynaktaki `ros2 topic hz` ile bu satırdaki Hz arasındaki fark doğrudan
taşımada kaybedilen karedir. Oran düşükse `depth_qos_depth` artırılabilir,
ZED'den daha düşük çözünürlüklü/hızlı derinlik istenebilir.

### Örnekleme

Kutunun ortasındaki `depth_roi_ratio` oranlı bölge örneklenir; kenarlar
direğe, gökyüzüne, arkadaki binaya taşar. `NaN/inf`, `0` ve menzil dışı
değerler atılır (yanan lamba, dokusuz yüzey ve CARLA'nın 1000 m'lik gökyüzü
burada elenir). Geçerli piksel oranı `depth_min_valid_ratio` altındaysa
**ölçüm reddedilir** — yarı dolu bir kutunun medyanı sessizce yanlış olur.
Kalanların **medyanı** alınır.

### Yedek

Derinlik geçersizse eski formüle düşülür, ama:

- sabitler yukarıdaki **ölçülmüş** değerler (362 / 218), yani yedek de
  derinlikle **aynı birimde** sonuç verir. Aynı alanda iki farklı ölçek
  dolaşması, bu değişiklikte kurtulunan hatanın ta kendisiydi;
- sonuç `src=0` ile **işaretlenir**, beyin ona ölçüm muamelesi yapmaz;
- `allow_bbox_fallback:=false` ile yedek tamamen kapatılabilir — o zaman
  ölçülemeyen tespit **hiç yayınlanmaz**.

Derinlik beklenip hiç gelmiyorsa düğüm 10 saniyede bir uyarır ve overlay'de
`DERINLIK YOK -> bbox tahmini` yazar. Sessiz düşme yok.

## Beyindeki eşikler

ID-3 gerçek metreye geçtiği için eşikler de ölçülen **2.0** çarpanıyla
çevrildi. **Sayılar değişti, aracın gerçek dünyada tetiklendiği mesafe
değişmedi** — yeniden ayar yapılmadı.

| durum | eski | yeni (metre) |
|---|---|---|
| kırmızı ışık → DUR | 9.0 | **4.5** |
| sarı ışık → yavaşla | 10.0 | **5.0** |
| DUR tabelası | 9.0 | **4.5** |
| yaya geçidi | 12.0 | **6.0** |
| durak | 10.0 | **5.0** |
| sola/sağa dön, ileri+sağ/sol | 12.0 | **6.0** |
| park | 10.0 | **5.0** |

## Simülasyon paritesi

`camera_overlay_node.py` occlusion için zaten bir CARLA depth kamerası
tutuyordu; artık onu `32FC1` (metre) olarak ROS'a da yayınlıyor
(`/carla/ego_vehicle/rgb_overlay/depth`). Böylece **simülasyon gerçek araçla
aynı kod yolunu** çalıştırıyor. `tabela_tespit_node`'un `depth_topic`
varsayılanı bilerek bu topic — `camera_topic` varsayılanıyla aynı kaynağı
göstermesi için. İkisi farklı kaynaklara bakarsa simülasyonda derinlik hiç
gelmez ve düğüm sessizce tahmine düşer.

Gerçek araçta **ikisi birden** repoint edilir:

```
ros2 run neuravix_ros2 tabela_tespit \
  -p camera_topic:=/zed/zed_node/rgb/image_rect_color \
  -p depth_topic:=/zed/zed_node/depth/depth_registered \
  -p camera_to_bumper:=<ölçülen>
```

## Araç günü kontrol listesi

1. **Derinlik gerçekten akıyor mu:**
   `ros2 topic hz /zed/zed_node/depth/depth_registered`
   — `node list` yetmez, takılı sürücüler topic reklamı yapıp hiçbir şey
   yayınlamaz (2026-07-13'te kanıtlandı).
2. **Encoding ve çözünürlük:** `ros2 topic echo --no-arr ... | head`
   → `32FC1` (metre) veya `16UC1` (mm) bekleniyor, çözünürlük RGB ile aynı
   olmalı. Farklıysa düğüm ölçekler ama bir kez göz atmak iyidir.
3. **Yayınlamıyorsa** araç ekibinden ZED launch'ında `depth_mode`
   (`NONE` olmamalı) ve depth yayınının açılması istenecek — sensör bringup
   bizde değil, `smart_can_stuff can_launch.xml`'de.
4. **`camera_to_bumper` ölçülüp verilmeli** (ZED optik merkezi → ön tampon).
5. Overlay'de kutuların yanındaki `(ZED)` etiketi ve bilgi kutusundaki
   `Mesafe:` satırı doğrulama için yeterli.

## Derleme uyarısı

`--symlink-install` bu pakette **symlink kurmuyor, kopyalıyor** (setuptools
sürümü nedeniyle `setup.py develop` yerine kopyalamaya düşüyor). Yani her
kaynak değişikliğinden sonra yeniden derlemek şart, yoksa düğüm sessizce eski
kodu çalıştırır — bu bir kez zaten yaşandı ve düzeltilmiş bir hata düzeltilmemiş
gibi göründü. Kontrol:

```bash
diff -q src/neuravix_ros2/neuravix_ros2/tabela_tespit_node.py \
        install/neuravix_ros2/lib/python3.10/site-packages/neuravix_ros2/tabela_tespit_node.py
```

Ayrıca bu makinede `smart_can_msgs` derlemesi `setuptools 84` ile
`python3-packaging 21.3` uyuşmazlığı yüzünden düşüyordu; `packaging>=24`
kullanıcı dizinine kurularak çözüldü (`pip install --user -U 'packaging>=24'`,
apt paketi bozulmadan gölgelenir).

## Araçlar

- `tools/derinlik_mesafe_testi.py` — ROS grafiği olmadan mesafe mantığını
  sınar (derinlik örnekleme, yedeğe düşme, encoding, beyin eşikleri).
- `tools/tabela_mesafe_kalibre.py` — bag'den ölçüm:
  `--mod hareket` derinlik kayıtta yokken bile gerçek sabiti çıkarır,
  `--mod derinlik` ZED derinliğini bbox tahminiyle yan yana basar.
