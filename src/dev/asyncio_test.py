import asyncio
import time

time_log = []

async def my_function():
    time_log.append(time.time())
    print("関数が実行されました。", time.ctime())
    # タスクの処理内容（ここでは1秒間非同期に待機）
    await asyncio.sleep(1)

async def main(interval, func, n):
    tasks = []
    for i in range(n):
        # タスクをスケジュール（ただし即時実行されるわけではない）
        task = asyncio.create_task(func())
        tasks.append(task)
        # 次のタスクの開始時刻まで非同期に待機
        await asyncio.sleep(interval)
    # すべてのタスクが完了するまで待つ
    await asyncio.gather(*tasks)

# 2秒間隔でmy_functionを5回実行する
asyncio.run(main(2, my_function, 5))

for i in range(len(time_log) - 1):
    print(time_log[i + 1] - time_log[i])