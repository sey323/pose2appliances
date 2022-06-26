import argparse
import logging
import time

import cv2

from appliances import NatureRemo
from enums import Gesture
from model import GestureDetector, PoseEstimator

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


def call_apliance(gesture: Gesture, appliance: NatureRemo) -> None:
    """検出されたジェスチャーの種類によって任意の家電を操作する。

    Args:
        gesture (Gesture): 検出されたジェスチャー
        appliance (NatureRemo): 操作する家電のコントローラークラス
    """
    if gesture == Gesture.NO_GESTURE:
        return 0

    if gesture == Gesture.LEFT_WRIST_UP:
        logger.info("リビングの電気を点灯させます")
        appliance.send_living_room_light()

    # 家電を操作した後は3秒停止する。
    # time.sleep(3)


def main(api_token: str, video_num: int, show_window: bool) -> None:
    pe = PoseEstimator()  # 関節の検出に利用するモデルを選択する。
    gd = GestureDetector(threshold=0.5)  # ジェスチャーを検出する。
    remo = NatureRemo(api_token=api_token)  # 操作する製品

    # USBカメラ
    cap = cv2.VideoCapture(video_num)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 256)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 256)
    logger.info("ビデオを有効化しアプリケーションを開始します。")

    while True:
        _, img = cap.read()

        # keypointを取得
        keypoints = pe.predict(img)

        # keypointからジェスチャーの内容を取得する。
        gesture = gd.check_gesture(keypoint=keypoints[0][0])
        call_apliance(gesture, appliance=remo)

        # 可視化する。
        if show_window:
            cv2.imshow("Video", pe.draw_prediction_on_image(img, keypoints=keypoints))

            # qを押すと止まる。
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


if __name__ == "__main__":
    # 引数の設定
    parser = argparse.ArgumentParser()

    parser.add_argument("api_token", help="NatureRemoから取得したAPIキー")
    parser.add_argument(
        "--video_num",
        default=0,
        help="利用するカメラモジュールの番号。ls /dev/video*で対象のビデオの番号を取得し、引数に指定する。default=0",
    )
    parser.add_argument(
        "--show", help="実行時にカメラモジュールの映像を画面に出力する場合は、こちらのオプションを付与する。", action="store_true"
    )
    args = parser.parse_args()

    main(api_token=args.api_token, video_num=args.video_num, show_window=args.show)
