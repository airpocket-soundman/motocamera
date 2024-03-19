import time
import threading
time_log = time.time()

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
            threading.Timer(interval, func_wrapper, [count]).start()  # 次の呼び出しをスケジュール

    func_wrapper(0)  # 関数呼び出しを開始

# テスト関数
def print_message(message):
    global time_log
    time_now = time.time()
    print(message, "at", time_now - time_log)
    time_log = time_now
# 例: 3回、2秒ごとにprint_messageを呼び出し、「Test message」というメッセージを出力
repeat_n_times(20, 0.05, print_message, "Test message")

