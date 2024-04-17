#ffmpegを使ってmp4エンコードし、メタデータ埋めてセーブするサンプルコード

import ffmpeg
import cv2
import numpy as np

# イメージデータのリストを作成する（サンプルとして）
# ここでは、640x480の黒い画像を100フレーム作成しています。
# 実際には、OpenCVで読み込んだり、生成した画像データを使用します。
frame_list = [np.zeros((480, 640, 3), np.uint8) for _ in range(100)]

# 動画ファイルの設定
width, height = 640, 480
fps = 16
output_file = 'output.mp4'

metadata_list = ["title=clockwork camera", "device=Bolex C-8 digitalized", "test code=test.py", "buffers=3", "queue=False",]
metadata_dict = {f"metadata:g:{i}": e for i, e in enumerate(metadata_list)}

# FFmpegのプロセスを設定
process = (
    ffmpeg
    .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(width, height), r=fps)
    .output(output_file, vcodec='libx264', pix_fmt='yuv420p', **metadata_dict)
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

# イメージデータをFFmpegにパイプ経由で送信
for frame in frame_list:
    process.stdin.write(
        frame.astype(np.uint8).tobytes()
    )

# パイプを閉じて、処理を終了
process.stdin.close()
process.wait()