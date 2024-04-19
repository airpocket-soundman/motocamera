# Raspberry Pi Zero2 W のmicroSDセットアップ方法

|項目|要件|
|-|-|
|SBC|Raspberry Pi Zero2 W|
|microSD|32GB以上|
|OS|Bullseye 64bit lite|

# OS version
OS:Raspberry Pi OS Bullseye 64bit lite

```
$ lsb_release -a
No LSB modules are available.
Distributor ID: Debian
Description:    Debian GNU/Linux 11 (bullseye)
Release:        11
Codename:       bullseye

$ getconf LONG_BIT
64
```

# USB SSHの有効化
config.txtに追記
dtoverlay=dwc2

commandline.txtのrootwait とquietの間に[]の中を追記
rootwait [modules-load=dwc2,g_ether] quiet

USB SSH化推奨

USB OTGするときは左側のmicro USBコネクタ

windowsにドライバインストールすること

# wifi setting
```
sudo raspi-config
```
1 System Options -> S1 Wireless LAN
SSIDとPassphraseを入力

# networkの設定
sudo raspi-config
 1 System Options -> S1 Wireless Lan

sudo reboot


# setup
```
sudo apt update & sudo apt -y upgrade
sudo apt -y install python3-dev python3-pip
sudo pip install picamera2
sudo pip install opencv-python
sudo apt -y install libgl1-mesa-dev
```


## カメラ設定
### IMX219 (camera V2の場合)
```
sudo nano /boot/config.txt
```

dtoverlay=imx219

```
sudo raspi-config
```
3 Interface Options -> I1 Legacy Camera -> No


### IMX708 (camera V3の場合)

```
sudo nano /boot/config.txt
```

dtoverlay=imx708


## swap無効化とtempのRAMディスク化
```
sudo systemctl stop dphys-swapfile
sudo systemctl disable dphys-swapfile
```
ファイルシステムの設定を書き換えて/tmpをRAM上にマウントする
```
sudo nano /etc/fstab
```
以下の行を追加
```
tmpfs /tmp tmpfs defaults,size=128m,noatime,mode=1777 0 0
```
microSD上の/tmpを削除する
```
sudo rm -rf /tmp
```
```
$ free -m
               total        used        free      shared  buff/cache   available
Mem:             419          73         193           0         151         292
Swap:              0           0           0
df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        29G  1.9G   26G   7% /
devtmpfs         80M     0   80M   0% /dev
tmpfs           210M     0  210M   0% /dev/shm
tmpfs            84M  928K   83M   2% /run
tmpfs           5.0M  4.0K  5.0M   1% /run/lock
tmpfs           128M     0  128M   0% /tmp
/dev/mmcblk0p1  255M   31M  225M  13% /boot
tmpfs            42M     0   42M   0% /run/user/1000
```
## Flaskのインスト―ル
```
pip install flask
```
flaskでapp.pyを実行するには
```
flask run --host=0.0.0.0
```

## sambaサーバー
```
sudo apt install samba
mkdir /home/[user]/share
sudo chmod 777 /home/[user]/share
sudo nano /etc/samba/smb.conf
```
追記
```
[share]
   comment = user file space
   path = /home/[user]/share
   force user = [user]
   guest ok = yes
   create mask = 0777
   directory mask = 0777
   read only = no

```
sudo systemctl restart smbd

## ffmpegのインストール
mpegのメタデータ埋め込みにffmpegを使用
python用のラッパーも入れておく
```
sudo apt install ffmpeg
suod pip install ffmpeg-python
```

## vim
sudo apt install vim

vim ~/.vimrc

set number
syntax enable
set expandtab
set tabstop=4
set shiftwidth=4

## data保存フォルダをマウントする
FAT32もしくはexFATでフォルダをマウントすることで、Win上からも直接読み込めるデータフォルダを作成する。
