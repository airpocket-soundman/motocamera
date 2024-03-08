import cv2
from picamera2 import Picamera2
import os
import time
import shutil
import threading

image_list = []
time_list = []

cap_width  =  640 	#640(defo), 320(high speed)
cap_height =  480	#480(defo), 240(high speed)

#IMX708
raw_width  =  2304	#4608(f), 2304(full/defo), 1536, 320(high speed)
raw_height =  1296	#2592(f), 1296(full/defo),  864, 240(high speed)

#IMX219
#raw_width  = 1640	#3280(f), 1640(full/defo), 1280, 320(high speed)
#raw_height = 1232	#2464(f), 1232(full/defo),  720, 240(high speed)

exposure_time = 5000	# 1000-100000  defo:5000
analog_gain   = 10.0		# 1.0-20.0    defo:5.0

tmp_folder_path     = "/tmp/img/"
share_folder_path   = "~/share/"
movie_file_name     = "test.mp4"
movie_file_path     = os.path.expanduser(share_folder_path + movie_file_name)
codec = cv2.VideoWriter_fourcc(*'mp4v')
record_fps = 16

test_frame_times = 100
frame_counter = 0

def get_images(image_index, camera):
    start_time = time.time()
    frame = camera.capture_array()	
    cv2.imwrite(tmp_folder_path + "image_" + str(image_index) + ".jpg", frame)	
    #frame_counter += 1
    elapsed_time = time.time() - start_time
    time_list.append(elapsed_time)

def movie_save():

    #video = cv2.VideoWriter(share_folder_path + movie_file_name, codec, record_fps, (cap_width, cap_height))
    video = cv2.VideoWriter(movie_file_path, codec, record_fps, (cap_width, cap_height))
    if not video.isOpened():
        print("can't be opened")
        sys.exit()
    for i in range(test_frame_times):
        frame = cv2.imread(tmp_folder_path + "image_" + str(i) + ".jpg")
        video.write(frame)
    video.release()

    
if not os.path.exists(tmp_folder_path):
    # フォルダが存在しない場合は作成
    os.makedirs(tmp_folder_path)
    print(f'{tmp_folder_path}を作成しました。')
else:
    print(f'{tmp_folder_path}は既に存在しています。')

camera = Picamera2()
config      = camera.create_preview_configuration(main={"format": 'RGB888', "size":(cap_width, cap_height)}, raw   ={"size":(raw_width, raw_height)}) 
#config_test = camera.create_preview_configuration(main   = {"size":(cap_width, cap_height), "format": 'RGB888'}, 
#                                                  raw    = {"size":(raw_width, raw_height)}, 
#                                                  lores  = {"size":(cap_width, cap_height)}, 
#:                                                  encode = "lores")
camera.configure(config)
camera.set_controls({"ExposureTime": exposure_time, "AnalogueGain": analog_gain})
camera.start()

threads = []
for i in range(test_frame_times):
    
    t = threading.Thread(target = get_images, args=(i, camera))    
    t.start()
    threads.append(t)
    time.sleep(0.030)
    if (i == 0):
        time.sleep(0.1)
    
for t in threads:
    t.join()

movie_save()

print(time_list)