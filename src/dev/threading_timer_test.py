#タイマー割り込みの精度と、割り込みプロセスの時間的影響の確認
# threading_timerでは、timer時間＋関数の処理時間が実行間隔になる。


import threading
import time

time_log = 0

def repeat_function(n, interval, callback, current_count=0):


    if current_count < n:
        callback()
        current_count += 1
        threading.Timer(interval, repeat_function, args=[n, interval, callback, current_count]).start()
    else:
        print("終了します。")

# 繰り返す関数の例
def my_function():
    global time_log
    now = time.time()

    print("関数が実行されました。")
    print(now - time_log)
    time.sleep(1)
    time_log = now

# 関数を5回、2秒間隔で繰り返す
repeat_function(5, 2, my_function)