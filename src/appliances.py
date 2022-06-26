import argparse

import requests


class NatureRemo:
    def __init__(self, api_token) -> None:
        self.api_token = api_token

    def send_living_room_light(self) -> None:
        """リビングの電気をつける
        Args:
            api_key (str): NatureRemoから取得するAPIToken
        """
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + self.api_token,
        }
        response = requests.post(
            "https://api.nature.global/1/appliances/${自宅にあるNatureRemoに登録した電球のID}/light",
            headers=headers,
            data="button=on",
        )
        return response.json()


if __name__ == "__main__":
    import argparse

    # デバック用パッケージ
    from icecream import ic

    # 引数の設定
    parser = argparse.ArgumentParser()

    parser.add_argument("api_token", help="NatureRemoから取得したAPIキー")

    args = parser.parse_args()

    remo = NatureRemo(api_token=args.api_token)

    ic(remo.send_living_room_light())
