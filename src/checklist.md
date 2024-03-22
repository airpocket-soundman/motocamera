# メモなど

・エンコードをffmpegに変更し、任意のmetadataを埋め込む。
・撮影完了判定をメインループではなくタイマーで行う。
・ラズパイとセンサのタイムスタンプのずれを測定する。
・上記を見込んだシャッターシンクロロジックを考える



# 参考データ
## mp4メタデータ例
参考
Title: タイトル
Subtitle: 字幕
Rating: 評価
Tags: タグ
Comments: コメント
Directors: 監督
Producers: プロデューサー
Writers: 脚本家
Year: 年
Length: 長さ（動画の再生時間）
Bit rate: ビットレート
Protected: 保護されているかどうか
Camera maker: カメラメーカー
Camera model: カメラモデル
F-stop: 絞り値
Exposure time: 露光時間
ISO speed: ISOスピード
Exposure bias: 露出バイアス
Focal length: 焦点距離
Max aperture: 最大絞り値
Metering mode: 測光モード
Flash mode: フラッシュモード
35mm focal length: 35mm換算焦点距離
Authors: 著者
Date taken: 撮影日
Date acquired: 取得日
Copyright notice: 著作権表示
Frame width: フレーム幅
Frame height: フレーム高さ
Total bitrate: 総ビットレート
Frame rate: フレームレート
Orientation: 方向
Media created: メディアの作成日
Resolution: 解像度
Color space: 色空間