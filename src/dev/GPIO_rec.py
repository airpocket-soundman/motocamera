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
# timer_rec.pyを改変してGPIO割り込みで撮影するようにする


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
import libcamera
import numpy as np

timelog = time.time()

number_still        = 0
number_cut          = 0
number_frame        = 0
raw_size            = 4     #0:1640 x 1232      1:2304 x 1296      2:3280 x 2464   3:4608 x 2592  4:320 x 240   0:IMX219 cine, 1:IMX708 cine 2:IMX219 still 3:IMX708 still
raw_pix             = [[1640, 1232], [2304, 1296], [3280, 2464], [4608, 2592], [320, 240]]
rec_size            = 4     #0: 640 x  480      1: 640 x  480      2:3280 x 2464   3:4608 x 2592  4:320 x 240   4:high speed cine
rec_pix             = [[ 640,  480], [ 640,  480], [3208, 2464], [4608, 2592], [320, 240]]
time_log            = []
time_log2           = []
time_log3           = []
time_log4           = []
time_camera         = []
exposure_time       = 2000  # 1000-100000  defo:5000
analogue_gain       = 16	# 1.0-20.0    defo:2.0
shutter_delay_time  = 0 * 0.001   # シャッター動作を検出してから画像取得するまでの遅延時間 ms

threads             = []    #マルチスレッド管理用リスト
frame_list          = []    #動画用画像保存リスト
exposure_time_list  = []

camera_mode         = 0     #0:movie,   1:still
speed_mode          = 0     #0:nomal,   1:high speed
gain_mode           = 0     #-1,0,1
film_mode           = 0     #0:mono,    1:mono,     2:color,    3:color,
is_shooting         = False
recording_completed = True

buffers             = 1
meta_data           = False
queue_control       = True

# Bolex
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


rec_finish_threshold_time    = 1        #sec  *detect rec button release
number_max_frame    = 100               #連続撮影可能な最大フレーム数　とりあえず16FPS x 60sec = 960フレーム
record_fps          = 16                #MP4へ変換する際のFPS設定値
tmp_folder_path     = "/tmp/img/"
share_folder_path   = os.path.expanduser("~/share/")
device_name         = "motocamera"
codec               = cv2.VideoWriter_fourcc(*'mp4v')
camera = Picamera2()

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

    config  = camera.create_still_configuration(
        main    = {
            "format"    : "RGB888", 
            "size"      : (rec_width, rec_height)
        }, 
        raw     = {
            "format"    : "SBGGR10_CSI2P",
            "size"      : (raw_width, raw_height)
        },
        buffer_count    = buffers,
        queue           = queue_control,
        controls        = {
            "ExposureTime"          : exposure_time, 
            "AnalogueGain"          : analogue_gain,
            "FrameDurationLimits"   : (100, 100000),
            "Sensitivity"           : 100
        },
        transform       = libcamera.Transform(hflip=1, vflip=1)
    )


    camera.configure(config)
    camera.start()

# timerを受けて画像を取得する関数
def shutter(text):
    global number_frame,time_log,time_log2,time_log3,is_shooting,time_camera,meta_data
    
    if number_frame < number_max_frame:
        is_shooting = True
        print("shutter")
        time_log.append(time.time())
        #time.sleep(shutter_delay_time)
        frame = camera.capture_array()
        time_log2.append(time.time())
        if meta_data:
            time_camera.append(camera.capture_metadata())
        frame_list.append(frame)
        time_log3.append(time.time())	
        number_frame += 1

# ムービー撮影後、画像を連結してムービーファイルを保存する。
def movie_save():
    global number_frame, number_cut, recording_completed,frame_list
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
        frame = frame_list[i]
        if film_mode == "mono":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        video.write(frame)
    print("movie rec finished")
    video.release()
    recording_completed = True
    number_cut += 1
    number_frame = 0
    frame_list = []

def repeat_n_times(n, interval, function, *args):
    """
    指定された回数n回、指定された間隔interval秒ごとに関数を呼び出します。

    Parameters:
    - n: 関数を呼び出す回数
    - interval: 関数を呼び出す間隔（秒）
    - function: 呼び出される関数
    - args: 関数に渡される引数
    """
    def func_wrapper(count):
        if count < n:  # 指定された回数まで関数を呼び出す
            function(*args)  # 関数を呼び出し
            count += 1  # 呼び出し回数をインクリメント
            threading.Timer(interval, func_wrapper, [count]).start()  # 次の呼び出しをスケジュール

    func_wrapper(0)  # 関数呼び出しを開始


# メイン
if __name__ == "__main__":
    if not os.path.exists(tmp_folder_path):
        # フォルダが存在しない場合は作成
        os.makedirs(tmp_folder_path)
        print(f'{tmp_folder_path}を作成しました。')
    else:
        print(f'{tmp_folder_path}は既に存在しています。')
        \
    # シェアフォルダ内の動画、静止画ファイルの最大番号を取得
    find_max_number_in_share_folder()
    print("動画と静止画の最大番号は",number_cut,number_still)

    set_camera_mode()
    
    # シャッター動作検出時のコールバック関数
    GPIO.add_event_detect(pin_shutter,  GPIO.RISING,    callback = shutter, bouncetime = 5)


    while(True):
        time.sleep(1)

        if is_shooting:
            if time.time() - time_log[-1] >= rec_finish_threshold_time:
                is_shooting = False
        
        else:
            if number_frame > 0:
                movie_save()
                for i in range(len(time_log)-1):
                    print((time_log[i + 1] - time_log[i]) * 1000,":",(time_log2[i]-time_log[i])* 1000,(time_log3[i]-time_log[i])* 1000)
                
                if meta_data:
                    for i in range(len(time_log)-1):
                        print((time_camera[i + 1]["SensorTimestamp"] - time_camera[i]["SensorTimestamp"]) / 1000000) #,exposure_time_list[i])

                
                time_log    = []
                time_log2   = []
                time_log3   = []
                time_log4   = []
                time_camera = []
