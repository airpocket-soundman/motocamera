import cv2
import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2

camera = Picamera2()
current_controls = camera.controls

# 現在のISO感度を表示
print(f"Current ISO Sensitivity: {current_controls['Sensitivity']}")

# 現在のホワイトバランスのゲイン値を表示
print(f"Current White Balance Gains: {current_controls.get('ColourGains', 'Not Available')}")

# 現在のシャッタースピードを表示
print(f"Current Shutter Speed: {current_controls.get('ExposureTime', 'Not Available')}")
config = camera.create_preview_configuration()
print(config)
config = camera.create_still_configuration()
print(config)
config = camera.create_video_configuration()
print(config)
camera.configure(config)