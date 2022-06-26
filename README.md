# 概要

カメラに写る人のポーズを検出し、ポーズの種類によって家電を操作します。

## 前準備

### NatureRemo の API キーの発行

以下の URL より、自宅の NatureRemo の API キーを発行する。

- [Nature Remo](https://home.nature.global/)

### 必要ライブラリのインストール

ローカルで実行する場合、必要なライブラリをインストールするために、以下のコマンドを実行する。

```sh:
pip install -r requirements.txt
```

## 起動

前準備出発行した NatureRemo の API キーを引数として、以下のコマンドを実行する。

```sh:
python src/main.py ${APIキー}
```

コマンドのそれぞれのオプションを以下に示す。

```sh:
python src/main.py -h

usage: main.py [-h] [--video_num VIDEO_NUM] [--show] api_token

positional arguments:
  api_token             NatureRemoから取得したAPIキー

optional arguments:
  -h, --help            show this help message and exit
  --video_num VIDEO_NUM
                        利用するカメラモジュールのid。ls /dev/video*で対象のビデオのidを取得し、引数に指定する。default=0
  --show                実行時にカメラモジュールの映像を画面に出力する場合は、こちらのオプションを付与する。
```

### コンテナ実行

本プログラムを Docker のコンテナ上で起動する場合は以下のコマンドを実行する。

```sh:
make build
make run API_KEY=${NatrueRemoのAPIキー} VIDEO_PATH=/dev/video0
```

`VIDEO_PATH`に指定するパスは以下のコマンドを実行し、PC に接続されているカメラモジュールを確認する。その後利用するカメラモジュールの絶対パスを指定する。

```sh:
ls -la /dev/video*
```
