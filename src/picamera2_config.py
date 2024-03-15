import cv2
import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2

camera = Picamera2()
config = camera.create_preview_configuration()
print(config)
config = camera.create_still_configuration()
print(config)
config = camera.create_video_configuration()
print(config)
camera.configure(config)