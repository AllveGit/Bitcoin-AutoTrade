import schedule
import requests
import json
import time
import threading
from SystemPkg.DefaultConfig import DefaultConfig

class KakaoLogWorker(threading.Thread):
    token_json_path = "configs/token_kakao.json"
    token_access_code = "access_token"
    token_refresh_code = "refresh_token"

    def __init__(self):
        super().__init__()

        self.rest_api_key = DefaultConfig.GetKakaoInfo()
        self.Alive = True

        # 카카오톡 토큰파일 읽어오기
        with open(self.token_json_path, "r") as fp:
            self.tokens = json.load(fp)

        # 토큰 갱신
        self.refresh_token()

        # 매 3시간마다 토큰갱신하도록 설정
        schedule.every(3).hours.do(self.refresh_token)

    def run(self):
        while self.Alive: 
            schedule.run_pending()
            time.sleep(1)

    def close(self):
        self.Alive = False
        schedule.cancel_job(self.refresh_token)

    # 카카오톡 토큰을 갱신하는 함수
    def refresh_token(self):
        """
        카카오톡의 Access Token은 REST API를 사용하였을 때 유효기간이 고작 6시간에 불과하며,
        Refresh Token의 유효기간은 2개월이고 유효기간 1달 남은 시점부터 갱신이 가능하다.

        그러므로 꾸준히 갱신이 필요하다.
        """

        token_refresh_url = "https://kauth.kakao.com/oauth/token"
        reqData = {
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": self.tokens[self.token_refresh_code]
        }

        response = requests.post(token_refresh_url, data=reqData)
        result = response.json()

        if self.token_access_code in result:
            self.tokens[self.token_access_code] = result[self.token_access_code]
        if self.token_refresh_code in result:
            self.tokens[self.token_refresh_code] = result[self.token_refresh_code]

        with open(self.token_json_path, "w") as fp:
            json.dump(self.tokens, fp)

        print(self.tokens)

    # 카카오톡 메시지를 보내는 함수
    def send_to_kakao(self, text):
        kakao_send_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

        headers={
            "Authorization" : "Bearer " + self.tokens[self.token_access_code]
        }

        data={
            "template_object": json.dumps({
                "object_type":"text",
                "text":text,
                "link":{
                    "web_url":"www.naver.com"
                }
            })
        }

        response = requests.post(kakao_send_url, headers=headers, data=data)
        if response.json().get('result_code') == 0:
            print("카카오톡 메시지를 성공적으로 보냈습니다.")
        else:
            print("카카오톡 메시지를 성공적으로 보내지 못했습니다. 오류메시지 : " + str(response.json()))

        # print(response.status_code)

        

    