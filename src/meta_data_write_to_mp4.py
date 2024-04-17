# mp4ファイルを読み込んで、任意のmetadataを追加するコード
import ffmpeg

input_file = '/home/airpocket/share/motocamera/input.mp4'
output_file = '/home/airpocket/share/motocamera/output_with_metadata.mp4'

# メタデータを定義
metadata = {
    'title': 'Your Title',
    'artist': 'Your Name',
    'test': 'test data'
}

metadata_list = ["title=My Title", "artist=Me", "album=X", "year=2019",]
metadata_dict = {f"metadata:g:{i}": e for i, e in enumerate(metadata_list)}


# メタデータを埋め込む
# メタデータを埋め込む
(
    ffmpeg
    .input(input_file)
    .output(output_file, **metadata_dict)
    .run()
)