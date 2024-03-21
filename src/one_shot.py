import cv2
import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2

num = 10

rec_width           = 640
rec_height          = 480
raw_width           = 2304          #2304
raw_height          = 1296          #1296
exposure_time       = 5000
analogue_gain       = 16
frame_list          = []
meta_list           = []
camera_time_list    = []
start_time_list     = []
finish_time_list    = []

camera = Picamera2()
config  = camera.create_still_configuration(
    main = {
        "format": 'RGB888',
        "size":(rec_width, rec_height)
    }, 
    raw = {
        "size":(raw_width, raw_height)
    }, 
    buffer_count = 4, 
    queue = True,
    controls = {
        "ExposureTime": exposure_time, 
        "AnalogueGain": analogue_gain, 
        'FrameDurationLimits': (100, 100000)
    }
)

print(config)

camera.configure(config)
camera.start()

for i in range(num):
    start_time_list.append(time.time())
    frame_list.append(camera.capture_array())
    camera_time_list.append(camera.capture_metadata()["SensorTimestamp"])
    finish_time_list.append(time.time())

if num == 1:
    print(finish_time_list[0] - start_time_list[0])

else:
    for j in range(i - 1):
        print("1: {:.3f}, 2: {:.3f}, 3: {:.3f}".format(start_time_list[j + 1] - start_time_list[j], 
            (camera_time_list[j + 1] - camera_time_list[j]) / 1000000,
            finish_time_list[j] - start_time_list[j])
        )


for i in range(num):
    cv2.imwrite("image" + str(i).zfill(3) + ".jpg", frame_list[i])

"""
{   
    'SensorTimestamp': 15332376548000, 
    'ScalerCrop': (576, 0, 3456, 2592), 
    'ColourCorrectionMatrix': (1.5160636901855469, -0.48789119720458984, -0.02817092090845108, -0.3048640787601471, 1.4338014125823975, -0.1289389580488205, 0.0156540684401989, -0.6485655903816223, 1.6329172849655151), 
    'FocusFoM': 2453, 
    'ExposureTime': 4996, 
    'SensorTemperature': -20.0, 
    'AfPauseState': 0, 
    'LensPosition': 1.0, 
    'FrameDuration': 17849, 
    'AeLocked': True, 
    'AfState': 0, 
    'DigitalGain': 1.000623345375061, 
    'AnalogueGain': 16.0, 
    'ColourGains': (1.83571457862854, 2.0074353218078613), 
    'ColourTemperature': 4077, 
    'Lux': 49.46232604980469, 
    'SensorBlackLevels': (4096, 4096, 4096, 4096)
}
"""