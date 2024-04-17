# GPIOをトリガーにビデオモードで撮影する。
# シャッター除去モデル使用、シャッターシンクロはしない。
# IMX708をビデオモードで撮影
# IMX708 ビデオモード仕様 1080P 50FPS, 720p 100FPS, 480p 120FPS
# 1080P 1920 x 1080 / 720P /480P 640 x 480 or 854 x 480
# ※要画角変化
# ※stillmode では、最大4608x2592 2304x1296までは画角同じ。


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
rec_width               = 640
rec_height              = 480


# Bolex
pin_shutter             = 25    # shutter timing pickup

# GPIO設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_shutter,     GPIO.IN, pull_up_down = GPIO.PUD_UP)


is_recording            = False     #録画中フラグ
max_record_sec          = 10        # 最大撮影時間
record_fps              = 16        # MP4へ変換する際のFPS設定値
share_folder_path       = os.path.expanduser("~/share/test.mp4")
device_name             = "bolex"
codec                   = cv2.VideoWriter_fourcc(*'avc1')
last_shutter_time       = 0
shutter_release_threshold_time = 200        #msec シャッター開放判定の閾値
recording_start_time    = 0

def init_camera():
    global camera
    camera = Picamera2()
    video_config = camera.create_video_configuration(
        main={"size": (1920, 1080), "format": "YUV420", "frame_rate": 50},
        controls={
            "ExposureTime": 20000,
            "AnalogueGain": 1.0,
            "AwbMode": "auto",
            "Brightness": 50,
            "Contrast": 15,
            "Saturation": 20,
            "Sharpness": 10,
            "NoiseReductionMode": "high"
        },
        transform={"hflip": True, "vflip": True}
    )
    camera.configure(video_config)
    camera.start()

def shutter_detected(channel):
    global last_shutter_time, recording_start_time, is_recording
    current_time = int(time.perf_counter() * 1000)
    if not is_recording:
        camera.start_recording(share_folder_path)
        is_recording = True
        recoding_start_time = current_time
    last_shutter_time = current_time

def check_recording_status():
    global is_recording
    if is_recording:
        current_time = int(time.perf_counter() * 1000)
        if current_time - last_shutter_time > shutter_release_threshold_time or current_time - recording_start_time > max_record_sec * 1000:
            camera.stop_recording()
            camera.stop()
            is_recording = False

if __name__ == "__main__":
    init_camera()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin_shutter, GPIO.RISING, callback=shutter_detected, bouncetime=200)

    try:
        while True:
            check_recording_status()
            time.sleep(0.01)
    finally:
        GPIO.cleanup()