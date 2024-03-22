# カメラとラズパイのtimestampのスケールのずれを確認するコード
# あまりずれてなかった。

from picamera2 import Picamera2, Metadata
import time
import RPi.GPIO as GPIO

picam2 = Picamera2()

Duration = 1

config = picam2.create_still_configuration(main={"size": (640, 480)},raw={"size":(2304,1296)}, buffer_count=1,queue=True)
#config = picam2.create_still_configuration(main={"size": (640, 480)},raw={"size":(2304,1296)}, buffer_count=2,queue=True)
picam2.configure(config)
picam2.set_controls({"ExposureTime": 5000})
picam2.set_controls({"FrameDurationLimits": (Duration*1000, Duration*1000)}) # MAX 100FPS -> 10ms
picam2.start()

time_log1   = []
time_log2   = []
time_log3   = []
frame_list  = []
meta_list   = []

def shutter():
    global time_log0, time_log1, time_log2, frame_list, meta_list
    time_log1.append(time.time())
    request = picam2.capture_request()
    time_log2.append(time.time())
    frame_list.append(request.make_image("main"))
    meta_list.append(request.get_metadata())
    request.release()
    time_log3.append(time.time())

def print_log():
    global time_log1, time_log2, time_log3, frame_list, meta_list
    print('print log')
    for i in range(len(time_log1)-1):
        t1 = (time_log1[i + 1] - time_log1[i]) * 1000
        t2 = (meta_list[i + 1]["SensorTimestamp"] - meta_list[i]["SensorTimestamp"]) / 1000000
        t3 = (time_log2[i] - time_log1[i]) * 1000
        t4 = (time_log3[i] - time_log2[i]) * 1000
        t5 = (time_log1[i] - time_log1[0]) * 1000
        t6 = (meta_list[i]["SensorTimestamp"] - meta_list[0]["SensorTimestamp"]) / 1000000
        print(f'{t1:16.3f}' + ' / ' + f'{t2:15.3f}' + ' // ' + f'{t3:15.3f}' + ' / ' + f'{t4:12.3f}' + ' // ' + f'{t5:15.3f}' + ' / ' + f'{t6:12.3f}' + ' / ' + f'{t5 - t6:12.3f}')

    time_log1   = []
    time_log2   = []
    time_log3   = []
    frame_list  = []
    meta_list   = []

d = -1

for i in range(100):
    shutter()
    """
    if Duration <= 20:
        d = 1
    elif Duration >= 100:
        d = -1
    Duration += d
    picam2.set_controls({"FrameDurationLimits": (Duration*1000, Duration*1000)})
    """
    picam2.set_controls({"FrameDurationLimits": (Duration*1000, Duration*1000)})

print_log()



