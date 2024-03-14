import cv2
from picamera2 import Picamera2
import os
import time

image_list  = []
time_list   = []
cap_width   =  640 			#4608, 2304, 1536. 1153, 640,, 1152     1240
cap_height  =  480			#2592, 1296,  864,  648, 360,,  864      930
raw_width   = 1640
raw_height  = 1232
exposure_time = 5000	# 1000-100000  defo:5000
analog_gain   = 5.0		# 1.0-20.0    defo:5.0

folder_path = "/tmp/img/"
movie_file_name = "test.mp4"
codec = cv2.VideoWriter_fourcc(*'mp4v')
record_fps = 16

test_frame_times = 100
frame_counter = 0

#folder_path = "/home/airpocket/Workspace/picamera2_test/img"

def get_images():
    global frame_counter  
    start_time = time.time()
    frame = camera.capture_array()	
    cv2.imwrite(folder_path + "image_" + str(frame_counter) + ".jpg", frame)	
    elapsed_time = time.time() - start_time
    print("frame_number = " + str(frame_counter) + " / time = " + str(elapsed_time))
    time_list.append(elapsed_time)
    frame_counter += 1

def movie_save():

    video = cv2.VideoWriter(movie_file_name, codec, record_fps, (cap_width, cap_height))
    if not video.isOpened():
        print("can't be opened")
        sys.exit()
    for i in range(frame_counter):
        frame = cv2.imread(folder_path + "image_" + str(i) + ".jpg")
        video.write(frame)
    video.release()

    
if not os.path.exists(folder_path):
    # フォルダが存在しない場合は作成
    os.makedirs(folder_path)
    print(f'{folder_path}を作成しました。')
else:
    print(f'{folder_path}は既に存在しています。')

camera = Picamera2()
camera.rotation = 180
config  = camera.create_preview_configuration(main={"format": 'RGB888', "size":(cap_width, cap_height)}, raw   ={"size":(raw_width, raw_height)})
#config  = camera.create_preview_configuration(main={"format": 'RGB888', "size":(640, 480)}, raw   ={"size":(2304, 1296)}) 
#config["transform"] = libcamera.Transform(hflip=1, vflip=1)
camera.configure(config)
#config = camera.create_preview_configuration(main = {"format": 'XRGB8888', "size": (cap_width, cap_height)})
#config = camera.create_preview_configuration(main = {"size":(cap_width, cap_height)}, raw = {"size":(raw_width, raw_height)})
#camera.configure(config)
camera.set_controls({"ExposureTime": exposure_time, "AnalogueGain": analog_gain})
camera.start()

for i in range(test_frame_times):
    get_images()

movie_save()


print(time_list)
