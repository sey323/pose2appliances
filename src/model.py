import collections
import logging
from collections import deque

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

from enums import Gesture

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class PoseEstimator:
    """入力画像から骨格のキーポイントを返す。"""

    def __init__(self) -> None:
        # Download the model from TF Hub.
        model = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
        self.movenet = model.signatures["serving_default"]

    def predict(self, target_image: np.ndarray) -> np.ndarray:
        """RGB画像の入力から、その画像に映る1人の骨格のキーポイントを返す。

        Args:
            target_image (np.ndarray): 処理対象の画像

        Returns:
            np.ndarray: 検出されたキーポイント
        """
        # 推論できるように画像の整形
        image = tf.expand_dims(target_image, axis=0)
        image = tf.cast(tf.image.resize_with_pad(image, 192, 192), dtype=tf.int32)
        # Run model inference.
        outputs = self.movenet(image)
        # Output is a [1, 1, 17, 3] tensor.
        keypoints = outputs["output_0"]

        del outputs, image, target_image
        return keypoints.numpy()

    def draw_prediction_on_image(self, target_image: np.ndarray, keypoints: np.ndarray):

        from util import draw_prediction_on_image

        return draw_prediction_on_image(target_image, keypoints)


class GestureDetector:
    """キーポイントからジェスチャーを返す。"""

    def __init__(self, maxlen: int = 10, threshold: float = 0.2) -> None:
        self.queue = deque(maxlen=maxlen)
        self.threshold = threshold

    def check_gesture(self, keypoint: np.ndarray) -> Gesture:
        """キーポイントから該当するジェスチャーの種類を推定する。

        Args:
            keypoint (np.ndarray): 1人の人物の関節の座標

        Returns:
            Gesture: ジェスチャーの種類の列挙型(enums.pyを参照)
        """
        if self._left_wrist_up_cross(keypoint):  # 左手を上げている状態
            self.queue.append(Gesture.LEFT_WRIST_UP)
        else:  # 何も検出されなかったときはGestrueなし
            logger.debug("ジェスチャーなし")
            self.queue.append(Gesture.NO_GESTURE)
        return self._check_mod_gesture()

    def _check_mod_gesture(
        self,
    ) -> Gesture:
        """検出されたジェスチャーのキューから、最頻値のジェスチャーを返す。

        Returns:
            Gesture: ジェスチャーの種類
        """
        if len(self.queue) < self.queue.maxlen:
            # キューが満たされていないときは、ジェスチャーなしとする。
            return Gesture.NO_GESTURE
        counter = collections.Counter(self.queue)
        mod_gesture, mod_gesture_count = counter.most_common()[0]
        if mod_gesture_count < int(self.queue.maxlen * 0.8):
            # 最頻値のジェスチャーがキューサイズの80％以下の場合は、ジェスチャーなしとする。
            return Gesture.NO_GESTURE

        if mod_gesture != Gesture.NO_GESTURE:  # ジェスチャーが検出された場合は、キューをリセットする。
            logger.debug("ジェスチャーが検出されたので、キューをリセットします。")
            self.queue.clear()
        return mod_gesture

    def _left_wrist_up_cross(self, keypoint: np.ndarray) -> bool:
        """左手を上げている状態

        Args:
            keypoint (np.ndarray): AIで検出された各キーポイントの配列

        Returns:
            bool: 左手を上げている状態であると判別された時: True
        """
        nose_height = keypoint[0][0]
        nose_width = keypoint[0][1]
        nose_score = keypoint[0][2]
        left_wrist_height = keypoint[9][0]
        left_wrist_width = keypoint[9][1]
        left_wrist_score = keypoint[9][2]
        if nose_score < self.threshold and left_wrist_score < self.threshold:
            return False
        if nose_height > left_wrist_height and nose_width < left_wrist_width:
            logger.debug("左手を上げましました。")
            return True
        else:
            return False


if __name__ == "__main__":
    import argparse

    import cv2

    # 引数の設定
    parser = argparse.ArgumentParser()

    parser.add_argument("image_path", help="実験対象の画像へのパス")

    args = parser.parse_args()

    img = cv2.imread(args.image_path)

    # モデルの初期化
    pe = PoseEstimator()
    # 画像のキーポイントを取得
    keypoints = pe.predict(img)
    print(keypoints)

    # 実行結果を保存
    drwaed_img = pe.draw_prediction_on_image(img, keypoints=keypoints)
    cv2.imwrite(f"{args.image_path.split('.')[0]}_results.png", drwaed_img)

    # 出力
    h, w, _ = drwaed_img.shape
    concat_img = cv2.hconcat([cv2.resize(img, (w, h)), drwaed_img])
    cv2.imshow("smaple", concat_img)

    # キーが押されるまで待ち続ける。
    cv2.waitKey(0)
    cv2.destroyAllWindows()
