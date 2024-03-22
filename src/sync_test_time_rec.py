#time_rec.pyを改造して、shutter syncをテストする
# timerはshutter()の処理時間を考慮して65msecに近いタイミングで動く様に設定。
# 


import cv2
import os
import time
import RPi.GPIO as GPIO
import sys
from picamera2 import Picamera2
import threading
import re
import libcamera
import numpy as np

raw_size                = 1     #defo:1
raw_pix                 = [[ 640,  480], [2304, 1296]]
rec_size                = 1     #defo:1
rec_pix                 = [[ 320,  240], [ 640,  480], [ 960, 720], [1280, 960]]

time_log1               = []
time_log2               = []
time_log3               = []
time_log4               = []
meta_data_list          = []
sensor_time_stamp_list  = []
frame_list              = []

#PID用
error_list              = [0, 0, 0, 0, 0]

exposure_time           = 5000  # 1000-100000  defo:5000
analogue_gain           = 16	# 1.0-20.0    defo:2.0
frame_duration_limit    = 10
shutter_interval        = 65                #
last_shutter_duration   = frame_duration_limit
buffers                 = 2
queue_control           = True
dynamic_frame_duration  = True
v_sync_adjustment       = True


number_max_frame        = 100                #連続撮影可能な最大フレーム数　とりあえず16FPS x 60sec = 960フレーム
record_fps              = 16                #MP4へ変換する際のFPS設定値

share_folder_path       = os.path.expanduser("~/share/")
device_name             = "Bolex"
codec                   = cv2.VideoWriter_fourcc(*'avc1')
camera                  = Picamera2()

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
    global rec_width, rec_height, raw_width, raw_height
    camera.stop()
    

    raw_width   = raw_pix[raw_size][0]
    raw_height  = raw_pix[raw_size][1]
    rec_width   = rec_pix[rec_size][0]
    rec_height  = rec_pix[rec_size][1]


    print("raw_size :", raw_width, "x", raw_height, "   rec_size :", rec_width, "x", rec_height)

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
    global reference_time, last_shutter_duration, error_list
    deviation = 0
    #print(len(time_log1))
    if len(time_log1) == 1:
        # 初回シャッター時のラズパイ時間とセンサー時間の差
        reference_time = int((time_log1[-1] * 1000) - ((meta_data_list[-1]["SensorTimestamp"]) / 1000000))
    else:
        # シャッタインターバル
        t1 = (time_log1[-1] - time_log1[-2]) * 1000                                         
        # センサーインターバル
        t2 = (meta_data_list[-1]["SensorTimestamp"] - meta_data_list[-2]["SensorTimestamp"]) / 1000000
            ## 初回のシャッターから今回のシャッターまでの経過時間
        t3 = (time_log1[-1] - time_log1[0]) * 1000
            ## 初回のセンサーtimestampから今回のセンサーtimestampまでの経過時間 
        t4 = (meta_data_list[-1]["SensorTimestamp"] - meta_data_list[0]["SensorTimestamp"]) / 1000000
        # 概ねラズパイとセンサの時計の誤差
        t5 = t3 - t4
        
        # request処理時間
        t6 = (time_log2[-2] - time_log1[-2]) * 1000
        # その他処理時間
        t7 = (time_log3[-2] - time_log2[-2]) * 1000
        # 1サイクルの合計時間
        t8 = t6 + t7

        #今回のシャッター時間とセンサータイムスタンプの時間差
        t9 = int((time_log1[-2] * 1000) - ((meta_data_list[-2]["SensorTimestamp"]) / 1000000))
        #初回の時間差との差
        t10 =  t9 - reference_time

        t11 = t5 % t1

        if t11 > t1 / 2:
            t12 = t11 - t1
        else:
            t12 = t11
        error_list.append(t12)
        error_list.pop(0)

        print(f'{t1:8.2f}' + ' / ' + f'{t2:8.2f}' + ' / ' + f'{t5:8.2f}' + ' // ' + f'{t6:8.2f}' + ' / ' + f'{t7:8.2f}' + ' / ' + f'{t8:8.2f}'  + ' // ' + f'{t10:8.2f}' + ' / ' + f'{t11:8.2f}' + ' / ' + f'{t12:8.2f}')
        
        if dynamic_frame_duration:
            if len(time_log1) >= 3:
                last_shutter_duration = int((time_log1[-1] - time_log1[-2]) * 1000000)
            
            #垂直同期
            if v_sync_adjustment:
                if abs(t12) < 3:
                    t12 = 0
                

                sume = int(sum(error_list))
                print("v_sync", int(t12), sume)


                deviation = int(t12) * 50 + sume * 5
                

            print(len(time_log1),f"last_shutter_duration = {last_shutter_duration}, deviation = {deviation}")
            #error_pre = t12
            camera.set_controls({"FrameDurationLimits": (last_shutter_duration + deviation, last_shutter_duration + deviation)})


# timerを受けて画像を取得する関数
def timer_shutter(text):
    global time_log1, time_log2,time_log3, frame_list, meta_data_list
    time_log1.append(time.time())
    if len(time_log1) != 3:
        request = camera.capture_request()
    time_log2.append(time.time())
    if len(time_log1) != 3:
        frame_list.append(request.make_image("main"))
        meta_data_list.append(request.get_metadata())
    if len(time_log1) != 3:
        request.release()
    #print(len(frame_list))
    
    time_log3.append(time.time())
    change_frame_duration_limit()   
    if len(frame_list) == number_max_frame - 1:
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
        if i < 10:
            jpg_path = share_folder_path + device_name + f'{i:03d}' + ".jpg" 
            cv2.imwrite(jpg_path,frame)
    print("movie rec finished")
    print(f"raw_width       = {raw_width}")
    print(f"raw_height      = {raw_height}")
    print(f"rec_width       = {rec_width}")
    print(f"rec_height      = {rec_height}")
    print(f"exposure_time   = {exposure_time}")
    print(f"buffers         = {buffers}")
    print(f"queue_control   = {queue_control}")
    video.release()
    #print_log()

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
            itime = interval
            if len(time_log1) > 0:
                itime = interval - max(0, time_log3[-1] - time_log1[-1])
            threading.Timer(itime, func_wrapper, [count]).start()  # 次の呼び出しをスケジュール

    func_wrapper(0)  # 関数呼び出しを開始

def print_log():
    global time_log1, time_log2, time_log3, frame_list, meta_data_list, sensor_time_stamp_list
    print('print log')

    for i in range(len(meta_data_list)):
        sensor_time_stamp_list.append(meta_data_list[i]["SensorTimestamp"])

    for i in range(len(time_log1)-1):
        t1 = (time_log1[i + 1] - time_log1[i]) * 1000
        t2 = (sensor_time_stamp_list[i + 1] - sensor_time_stamp_list[i]) / 1000000
        t3 = (time_log2[i] - time_log1[i]) * 1000
        t4 = (time_log3[i] - time_log2[i]) * 1000
        t5 = (time_log1[i] - time_log1[0]) * 1000
        t6 = (sensor_time_stamp_list[i] - sensor_time_stamp_list[0]) / 1000000
        print(f'{t1:16.3f}' + ' / ' + f'{t2:15.3f}' + ' // ' + f'{t3:15.3f}' + ' / ' + f'{t4:12.3f}' + ' // ' + f'{t5:15.3f}' + ' / ' + f'{t6:12.3f}' + ' / ' + f'{t5 - t6:12.3f}')

    time_log1   = []
    time_log2   = []
    time_log3   = []
    frame_list  = []
    meta_data_list   = []


# メイン
if __name__ == "__main__":

    find_max_number_in_share_folder()
    print("動画と静止画の最大番号は",number_cut,number_still)

    set_camera_mode()

    # 例: 3回、2秒ごとにprint_messageを呼び出し、「Test message」というメッセージを出力
    repeat_n_times(number_max_frame, shutter_interval/1000, timer_shutter, "test")
    #repeat_n_times(20, 0.01, print_message, "Test message")

    while(True):
        time.sleep(100)
