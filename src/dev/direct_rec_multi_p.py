# Copyright (c) 2024 yasuhiro yamashita
# Released under the MIT license.
# see http://open source.org/licenses/MIT
#
# ========================================
# pathe motocamera digitlize mod controler
# controler program ver.0.0.0
# on Raspberry Pi Zero2W
# image sensor:IMX708
# ========================================
# imwriteをマルチプロセス化

import cv2
import os
import subprocess
import time
import datetime
import RPi.GPIO as GPIO
import sys
from picamera2 import Picamera2
import threading
import shutil
import re
from multiprocessing import Process
import libcamera

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

number_still        = 0
number_cut          = 0
number_frame        = 0
raw_size            = 0     #0:1640 x 1232      1:2304 x 1296      2:3280 x 2464   3:4608 x 2592  4:320 x 240   0:IMX219 cine, 1:IMX708 cine 2:IMX219 still 3:IMX708 still
raw_pix             = [[1640, 1232], [2304, 1296], [3280, 2464], [4608, 2592], [320, 240]]
rec_size            = 1     #0: 640 x  480      1: 640 x  480      2:3280 x 2464   3:4608 x 2592  4:320 x 240   4:high speed cine
rec_pix             = [[ 800,  600], [ 640,  480], [3208, 2464], [4608, 2592], [320, 240]]
time_log            = []
time_log2           = []
time_log3           = []
time_log4           = []
exposure_time       = 5000  # 1000-100000  defo:5000
analogue_gain       = 2.0	# 1.0-20.0    defo:2.0
shutter_delay_time  = 0 * 0.001   # シャッター動作を検出してから画像取得するまでの遅延時間 ms

threads = []

camera_mode         = 0     #0:movie,   1:still
speed_mode          = 0     #0:nomal,   1:high speed
gain_mode           = 0     #-1,0,1
film_mode           = 0     #0:mono,    1:mono,     2:color,    3:color,
is_shooting         = False
recording_completed = True


rec_finish_threshold_time    = 1      #sec  *detect rec button release
number_max_frame    = 960               #連続撮影可能な最大フレーム数　とりあえず16FPS x 60sec = 960フレーム
record_fps          = 16                #MP4へ変換する際のFPS設定値
tmp_folder_path     = "/tmp/img/"
share_folder_path   = os.path.expanduser("~/share/")
device_name         = "motocamera"
codec               = cv2.VideoWriter_fourcc(*'mp4v')
camera = Picamera2()

# GPIO設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_shutter,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_shutdown,    GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip1,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip2,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip3,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip4,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip5,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_dip6,        GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_led_red,     GPIO.OUT)
GPIO.setup(pin_led_green,   GPIO.OUT)

# shareフォルダの動画と静止画のファイル番号を読み取る
def find_max_number_in_share_folder():
    global number_still, number_cut
    # ファイル名の数字部分を抽出する正規表現パターン
    pattern_mp4 = re.compile(r'motocamera(\d{3})\.mp4$')
    pattern_jpg = re.compile(r'motocamera(\d{3})\.jpg$')
    number_cut   = -1  # 存在する数字の中で最も大きいものを保持する変数
    number_still = -1
    # 指定されたフォルダ内のすべてのファイルに対してループ
    for filename in os.listdir(share_folder_path):
        match_mp4 = pattern_mp4.match(filename)
        match_jpg = pattern_jpg.match(filename)
        if match_mp4:
            # ファイル名から抽出した数字を整数として取得
            number = int(match_mp4.group(1))
            # 現在の最大値と比較して、必要に応じて更新
            if number > number_cut:
                number_cut = number
        if match_jpg:
            number = int(match_jpg.group(1))
            if number > number_still:
                number_still = number
    
    number_still += 1
    number_cut   += 1

# dipスイッチの状態から殺遺影モードを読みとる
def read_mode(channel):
    print("GPIO = ", channel)
    global camera_mode, speed_mode, gain_mode, film_mode
    if GPIO.input(pin_dip1):                                    # movieモードの時
        camera_mode = 0
    elif not GPIO.input(pin_dip1):                              # stillモードの時
        camera_mode = 1

    if GPIO.input(pin_dip2):                                    # normalモードの時
        speed_mode = 0
    elif not GPIO.input(pin_dip2):                              # hight speedモードの時
        speed_mode = 1

    if       GPIO.input(pin_dip3) and     GPIO.input(pin_dip4): # gain = 2
        gain_mode =  0
    elif     GPIO.input(pin_dip3) and not GPIO.input(pin_dip4): # gain = 4
        gain_mode =  1
    elif not GPIO.input(pin_dip3) and     GPIO.input(pin_dip4): # gain = 8
        gain_mode =  2
    elif not GPIO.input(pin_dip3) and not GPIO.input(pin_dip4): # gain = 16
        gain_mode =  3

    if       GPIO.input(pin_dip5) and     GPIO.input(pin_dip6): # monocro
         film_mode = "mono"
    elif     GPIO.input(pin_dip5) and not GPIO.input(pin_dip6): # monocro
        film_mode = "mono"
    elif not GPIO.input(pin_dip5) and     GPIO.input(pin_dip6): # color
        film_mode = "color"
    elif not GPIO.input(pin_dip5) and not GPIO.input(pin_dip6): # color
        film_mode = "color"
    set_camera_mode()
    print_mode()

# 撮影モードをシリアル表示
def print_mode():
    if camera_mode == 0:
        print("camera_mode  : movie")
    elif camera_mode == 1:
        print("camera_mode  : still")

    if speed_mode == 0:
        print("speed_mode   : normal")
    elif speed_mode == 1:
        print("speed_mode   : high speed")
    
    print("gain         : ", gain_mode)
    print("film_mode    : ", film_mode)

# 撮影モードに応じてpicameraのconfigを設定する
def set_camera_mode():
    global rec_width, rec_height, raw_width, raw_height, shutter_delay_time
    camera.stop()
    
    if camera_mode == 0:
        if speed_mode == 0:
            raw_width   = raw_pix[raw_size][0]
            raw_height  = raw_pix[raw_size][1]
            rec_width   = rec_pix[rec_size][0]
            rec_height  = rec_pix[rec_size][1]
        elif speed_mode == 1:
            raw_width   = raw_pix[4][0]
            raw_height  = raw_pix[4][1]
            rec_width   = rec_pix[4][0]
            rec_height  = rec_pix[4][1]

    elif camera_mode == 1:
        raw_width   = raw_pix[3][0]
        raw_height  = raw_pix[3][1]
        rec_width   = rec_pix[3][0]
        rec_height  = rec_pix[3][1]

    print("raw_size :", raw_width, "x", raw_height, "   rec_size :", rec_width, "x", rec_height)
    config  = camera.create_preview_configuration(main={"format": 'RGB888', "size":(rec_width, rec_height)}, raw   ={"size":(raw_width, raw_height)})
    #config  = camera.create_preview_configuration(main={"format": 'RGB888', "size":(640, 480)}, raw   ={"size":(2304, 1296)}) 
    config["transform"] = libcamera.Transform(hflip=1, vflip=1)    
    camera.configure(config)
    camera.set_controls({"ExposureTime": exposure_time, "AnalogueGain": analogue_gain * (2 ** gain_mode)})
    camera.start()

# シャッター開を検出した場合の処理
def on_shutter_open(channel):
    global time_log, threads, number_frame, is_shooting
    time_log.append(time.time())
    if camera_mode == 0:
        if (number_frame <= number_max_frame and recording_completed == True):
            is_shooting = True
            
            #t = threading.Thread(target = get_images, args=(number_frame, camera))    
            #t.start()
            #threads.append(t)
            get_images(number_frame, camera)
            number_frame += 1
    
    if camera_mode == 1:
        get_still_image()

# シャットダウンボタンが押されたとき
def on_shutdown_button_pressed(channel):
    global number_cut, number_frame
    print("GPIO =", channel, "shutdown")
    #command = ["sudo", "shutdown", "-h", "now"]
    #subprocess.run(command)

def save_image_process(image_path, frame):
    global time_log5
    log5 = time.time()
    cv2.imwrite(image_path, frame)
    log6 = time.time()
    print(log6 - log5)

#ムービー用画像取得
def get_images(image_index, camera):
    global time_log2, time_log3, time_log4
    if recording_completed:
        time_log2.append(time.time())
        time.sleep(shutter_delay_time)
        frame = camera.capture_array()
        time_log3.append(time.time())	

        # マルチプロセスで画像保存
        image_path = tmp_folder_path + f"image_{image_index}.jpg"
        p = Process(target=save_image_process, args=(image_path, frame))
        p.start()

        time_log4.append(time.time())
    else:
        print("recording now")



#Still写真を撮る処理
def get_still_image():
    global number_still
    print("get still image")
    still_file_path = share_folder_path + device_name + "{:03}".format(number_still) + ".jpg"
    frame = camera.capture_array()
    if film_mode == "mono":
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(still_file_path, frame)
    print(still_file_path)
    number_still += 1

# ムービー撮影後、画像を連結してムービーファイルを保存する。
def movie_save():
    GPIO.output(pin_led_red, True)
    global number_frame, number_cut, recording_completed
    recording_completed = False
    print("save movie")
    movie_file_path = share_folder_path + device_name + "{:03}".format(number_cut) + ".mp4"

    if film_mode == "mono":
        video = cv2.VideoWriter(movie_file_path, codec, record_fps, (rec_width, rec_height), isColor = False)
    else:      
        video = cv2.VideoWriter(movie_file_path, codec, record_fps, (rec_width, rec_height))

    if not video.isOpened():
        print("can't be opened")
        sys.exit()
    for i in range(number_frame):
        frame = cv2.imread(tmp_folder_path + "image_" + str(i) + ".jpg")
        if film_mode == "mono":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        video.write(frame)
    print("movie rec finished")
    video.release()
    recording_completed = True
    number_cut += 1
    number_frame = 0
    GPIO.output(pin_led_red, False)

# メイン
if __name__ == "__main__":

    # LED点灯初期化
    GPIO.output(pin_led_green, True)
    GPIO.output(pin_led_red, False)

    # イメージ仮保存用フォルダが存在しない場合は作成
    if not os.path.exists(tmp_folder_path):
        os.makedirs(tmp_folder_path)
        print(f'{tmp_folder_path}を作成しました。')
    else:
        print(f'{tmp_folder_path}は既に存在しています。')

    # シャッター動作検出時のコールバック関数
    GPIO.add_event_detect(pin_shutter,  GPIO.RISING,    callback = on_shutter_open, bouncetime = 5)
    # リセットボタン検出時のコールバック関数
    GPIO.add_event_detect(pin_shutdown, GPIO.FALLING,   callback = on_shutdown_button_pressed, bouncetime = 100)
    # dipswitchが切り替わった時のコールバック関数
    GPIO.add_event_detect(pin_dip1,     GPIO.BOTH,    callback = read_mode, bouncetime = 5)
    GPIO.add_event_detect(pin_dip2,     GPIO.BOTH,    callback = read_mode, bouncetime = 5)
    GPIO.add_event_detect(pin_dip3,     GPIO.BOTH,    callback = read_mode, bouncetime = 5)
    GPIO.add_event_detect(pin_dip4,     GPIO.BOTH,    callback = read_mode, bouncetime = 5)
    GPIO.add_event_detect(pin_dip5,     GPIO.BOTH,    callback = read_mode, bouncetime = 5)
    GPIO.add_event_detect(pin_dip6,     GPIO.BOTH,    callback = read_mode, bouncetime = 5)

    # dipスイッチの状態を読み取り、撮影モード設定
    read_mode(99)

    # シェアフォルダ内の動画、静止画ファイルの最大番号を取得
    find_max_number_in_share_folder()
    print("動画と静止画の最大番号は",number_cut,number_still)

    while(True):
        time.sleep(1)

        # ムービー撮影完了を検出
        if is_shooting:
            if time.time() - time_log[-1] >= rec_finish_threshold_time:
                is_shooting = False
        
        # ムービー撮影完了後の処理
        else:
            if number_frame > 0:
                movie_save()
                for i in range(len(time_log)-1):
                    print(time_log[i + 1] - time_log[i],":",time_log3[i]-time_log2[i],":", time_log4[i]-time_log3[i])
                time_log  = []
                time_log2 = []
                time_log3 = []
                time_log4 = []

