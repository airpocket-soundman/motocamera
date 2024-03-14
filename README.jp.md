# Pathe motocamera デジタル化

このプロジェクトではpathe motocameraのデジタル化を行います。

# デジタル化ユニット仕様

|項目|仕様|
|-|-|
|イメージセンサ|IMX708|
|解像度|640x360(stillモード時4608x2592)|
|イメージカバー率|0.76(W)x0.55(H)|
|連続録画時間|60sec以上|
|最大FPS|16以上|
  
# dip switch
ユニット上のdip swichで各種設定ができます。

|No|設定項目|
|-|-               |
|1|撮影モード       |
|2|高速撮影モード    |
|3|gain設定         |
|4|gain設定         |
|5|フィルムモード設定|
|6|フィルムモード設定|

撮影モード設定
|SW1|設定|
|-|-|
|on |movie|
|off|still|

高速撮影モード設定
|SW2|設定|
|-|-|
|on|高速撮影モード(画像サイズ320x180)|

gain設定
|SW3|SW4|設定|
|-|-|-|
|off|off|自動|
|off|on | -1|
|on |off|  0|
|on |on | +1|


フィルムモード設定
|SW5|SW6|モード|
|-|-|-|
|off|off|モノクローム|
|off|on |モノクローム|
|on |off|カラー|
|on |on |カラー|

# GPIO設定
## motocamera
pin_shutter         = 23    # shutter timing picup 
pin_led_red         = 24
pin_led_green       = 25
pin_shutdown        =  8
pin_dip1            =  7
pin_dip2            =  1
pin_dip3            = 12
pin_dip4            = 16
pin_dip5            = 20
pin_dip6            = 21

## Bolex
pin_shutter         = 25    # shutter timing picup 
pin_led_red         = 15
pin_led_green       = 18
pin_shutdown        = 14
pin_dip1            =  8
pin_dip2            =  7
pin_dip3            =  1
pin_dip4            = 12
pin_dip5            = 16
pin_dip6            = 20