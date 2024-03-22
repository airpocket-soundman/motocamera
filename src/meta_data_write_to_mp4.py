import ffmpeg

input_file = 'input.mp4'
output_file = 'output_with_metadata.mp4'

# メタデータを定義
metadata = {
    'title': 'Your Title',
    'artist': 'Your Name'
}

# メタデータを埋め込む
# メタデータを埋め込む
(
    ffmpeg
    .input(input_file)
    .output(output_file, **{'metadata': 'title=' + metadata['title'], 'metadata': 'artist=' + metadata['artist']})
    .run()
)