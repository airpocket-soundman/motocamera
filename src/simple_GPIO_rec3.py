# FrameDurationLimitsを動的に変更させてシンクロを狙う

import cv2
import os
import time
import RPi.GPIO as GPIO
import sys
from picamera2 import Picamera2
import libcamera
import numpy as np

raw_width               = 2304           #2304
raw_height              = 1296           #1296
rec_width               = 320
rec_height              = 240
time_log                = []
time_log2               = []
time_log3               = []
frame_list              = []
meta_data_list          = []

exposure_time           = 5000              # 1000-100000  defo:5000
analogue_gain           = 16	            # 1.0-20.0    defo:2.0
frame_duration_limit    = 20
buffers                 = 1
queue_control           = False
dynamic_frame_duration  = True
v_sync_adjustment       = True
# Bolex
pin_shutter             = 25    # shutter timing pickup

# GPIO設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_shutter,     GPIO.IN, pull_up_down = GPIO.PUD_UP)

number_max_frame        = 100                 #連続撮影可能な最大フレーム数　とりあえず16FPS x 60sec = 960フレーム
record_fps              = 16                #MP4へ変換する際のFPS設定値
share_folder_path       = os.path.expanduser("~/share/")
device_name             = "bolex"
codec                   = cv2.VideoWriter_fourcc(*'avc1')
camera                  = Picamera2()

# 撮影モードに応じてpicameraのconfigを設定する
def set_camera_mode():
    global rec_width, rec_height, raw_width, raw_height
    camera.stop()

    config  = camera.create_still_configuration(
        main    = {
            "format"    : "BGR888", 
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
            "FrameDurationLimits"   : (frame_duration_limit * 1000, frame_duration_limit * 1000)
            #"FrameRate"             : 16.5 
        },
        transform       = libcamera.Transform(hflip=1, vflip=1)
    )

    camera.configure(config)
    camera.start()

def change_frame_duration_limit():
    deviation = 0
    if dynamic_frame_duration and len(time_log) > 1:
        last_shutter_duration = (time_log[-1] - time_log[-2]) * 1000000

    #垂直同期
    if v_sync_adjustment and len(time_log) > 1:
        deviation = (time_log2[-1] - time_log[-1]) * 1000000

    camera.set_controls({"FrameDurationLimits": (last_shutter_duration + deviation, last_shutter_duration * 1000)})

# timerを受けて画像を取得する関数
def shutter(text):
    global time_log, time_log2, time_log3, frame_list, meta_data_list
    
    if len(frame_list) < number_max_frame:
        time_log.append(time.time())
        request = camera.capture_request()
        time_log2.append(time.time())
        frame_list.append(request.make_image("main"))
        meta_data_list.append(request.get_metadata())
        request.release()
        change_frame_duration_limit()
        time_log3.append(time.time())
    else:
        movie_save()

# ムービー撮影後、画像を連結してムービーファイルを保存する。
def movie_save():
    global recording_completed, frame_list, meta_data_list
    recording_completed = False
    print("save movie")
    movie_file_path = share_folder_path + device_name + ".mp4"

    video = cv2.VideoWriter(movie_file_path, codec, record_fps, (rec_width, rec_height))

    if not video.isOpened():
        print("video writer can't be opened")
        sys.exit()
    for i in range(len(frame_list)):
        frame = np.array(frame_list[i])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video.write(frame)
    print("movie rec finished")
    print(f"raw_width       = {raw_width}")
    print(f"raw_height      = {raw_height}")
    print(f"rec_width       = {rec_width}")
    print(f"rec_height      = {rec_height}")
    print(f"exposure_time   = {exposure_time}")
    print(f"buffers         = {buffers}")
    print(f"queue_control   = {queue_control}")
    video.release()
    print_log()

def print_log():
    global time_log, time_log2, frame_list, meta_data_list

    print("  frame interval / camera interval // capture request / extract data  (msec)"  )
    for i in range(len(time_log)-1):
        t1 = (time_log[i + 1] - time_log[i]) * 1000
        t2 = (meta_data_list[i + 1]["SensorTimestamp"] - meta_data_list[i]["SensorTimestamp"]) / 1000000
        t3 = (time_log2[i] - time_log[i]) * 1000
        t4 = (time_log3[i] - time_log2[i]) * 1000
        print(f'{t1:16.3f}' + ' / ' + f'{t2:15.3f}' + ' // ' + f'{t3:15.3f}' + ' / ' + f'{t4:12.3f}')

    
    time_log            = []
    time_log2           = []
    frame_list          = []
    meta_data_list      = []

# メイン
if __name__ == "__main__":

    set_camera_mode()
    
    # シャッター動作検出時のコールバック関数
    GPIO.add_event_detect(pin_shutter,  GPIO.RISING,    callback = shutter, bouncetime = 1)

    while(True):
        time.sleep(10)

