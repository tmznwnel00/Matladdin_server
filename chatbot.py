# -*- coding: utf-8 -*-
import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            # 'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json'
            # 'Accept': 'text/event-stream'
        }

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-002',
                           headers=headers, json=completion_request, stream=True) as r:
            
            return r.json()


if __name__ == '__main__':
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key=os.getenv("API_KEY"),
        api_key_primary_val=os.getenv("API_KEY_PRIMARY_VAL"),
        # request_id='93482c82039b4981bf1cbecbce9d6278'
    )

    preset_text = [{"role":"system","content":"유저는 음식메뉴를 하나 고르려고해.\n많은 음식 메뉴 후보들 중에서 hcx-002가 물어보는 10개의 질문 대답에 따라 후보군을 줄여나갈거야.\n질문은 항상 하나씩 해주고, 이지선다로 내줘.\n그리고 질문은 특별한 상황을 예시로 들며 해줘.\n질문 예시 : 너무 일이 바쁜날, 혼자 먼저 음식 먹으러 가고싶어, 아니면 다른 사람들 기다렸다가 같이 먹으러 가고싶어?\n유저가 \"지금부터 질문할게\"를 말하면, 항상 초기화 해줘.\n선택지 두개는 항상 말 끝에 \"선택지:\"로 시작하고, '/'로 구분해서 말해줘.\n\n10개의 질문이 끝났을때는 이때까지 내가 한 답변을 종합하여, 단 하나의 음식을 추천해줘."},{"role":"user","content":"지금부터 질문할게"},{"role":"assistant","content":"네, 지금부터 질문을 드리겠습니다.\n\n1. 오늘은 스트레스 받는 날이야. 매운음식을 먹고싶어, 아니면 단 음식을 먹고싶어? 선택지: 매운음식/단 음식"},{"role":"user","content":"매운음식"},{"role":"assistant","content":"2. 오늘은 비가 오는 날이야. 따뜻한 국물 요리가 먹고싶어, 아니면 바삭한 전 요리가 먹고싶어? 선택지: 따뜻한 국물 요리/바삭한 전 요리"},{"role":"user","content":"바삭한 전 요리"},{"role":"assistant","content":"3. 오늘은 친구들과 만나는 날이야. 분위기 좋은 레스토랑에서 식사를 하고 싶어, 아니면 편안한 분위기의 카페에서 차를 마시고 싶어? 선택지: 분위기 좋은 레스토랑/편안한 분위기의 카페"},{"role":"user","content":"편안한 분위기의 카페"},{"role":"assistant","content":"4. 오늘은 다이어트 하는 날이야. 샐러드를 먹고 싶어, 아니면 닭가슴살을 먹고 싶어? 선택지: 샐러드/닭가슴살"},{"role":"user","content":"닭가슴살"},{"role":"assistant","content":"5. 오늘은 날씨가 더운 날이야. 시원한 냉면이 먹고 싶어, 아니면 이열치열 삼계탕이 먹고 싶어? 선택지: 시원한 냉면/이열치열 삼계탕"},{"role":"user","content":"이열치열 삼계탕"},{"role":"assistant","content":"6. 오늘은 우울한 날이야. 맛있는 파스타가 먹고 싶어, 아니면 달콤한 케이크가 먹고 싶어? 선택지: 맛있는 파스타/달콤한 케이크"},{"role":"user","content":"달콤한 케이크"},{"role":"assistant","content":"7. 오늘은 가족과 함께하는 날이야. 한식 아니면 양식을 먹고 싶어? 선택지: 한식/양식"},{"role":"user","content":"한식"},{"role":"assistant","content":"8. 오늘은 연인과 데이트하는 날이야. 스테이크와 와인을 먹고 싶어, 아니면 초밥과 사케를 먹고 싶어? 선택지: 스테이크와 와인/초밥과 사케"},{"role":"user","content":"스테이크와 와인"},{"role":"assistant","content":"9. 오늘은 회식하는 날이야. 삼겹살집 가고 싶어? 선택지: 삼겹살집/횟집"},{"role":"user","content":"삼겹살집"},{"role":"assistant","content":"10. 오늘은 생일이야. 미역국을 먹고 싶어, 아니면 피자를 먹고 싶어? 선택지: 미역국/피자"},{"role":"user","content":"미역국"},{"role":"assistant","content":"모든 질문에 대한 답변을 받았습니다. \n\n답변을 바탕으로 추천해드릴 음식은 '삼계탕'입니다. \n스트레스 받는 날 매운음식을 선호하며, 비오는 날에는 따뜻한 국물요리보다 바삭한 전 요리를 선호했습니다. 또한, 친구들과 만나는 날에는 편안한 분위기의 카페를 선호했으며, 다이어트 하는 날에는 닭가슴살을 선호했습니다. 그 외에도 이열치열 삼계탕, 달콤한 케이크, 한식, 스테이크와 와인, 삼겹살 등 다양한 음식을 선호했지만, 생일인 만큼 미역국을 추천해드립니다.  \n\n즐거운 식사시간 되세요!"}]

    request_data = {
        'messages': [{"role":"system","content":"유저는 음식메뉴를 하나 고르려고해.\n많은 음식 메뉴 후보들 중에서 hcx-002가 물어보는 10개의 질문 대답에 따라 후보군을 줄여나갈거야.\n질문은 항상 하나씩 해주고, 이지선다로 내줘.\n그리고 질문은 특별한 상황을 예시로 들며 해줘.\n질문 예시 : 너무 일이 바쁜날, 혼자 먼저 음식 먹으러 가고싶어, 아니면 다른 사람들 기다렸다가 같이 먹으러 가고싶어?\n유저가 \"지금부터 질문할게\"를 말하면, 항상 초기화 해줘.\n선택지 두개는 항상 말 끝에 \"선택지:\"로 시작하고, '/'로 구분해서 말해줘.\n\n10개의 질문이 끝났을때는 이때까지 내가 한 답변을 종합하여, 단 하나의 음식을 추천해줘."},{"role":"user","content":"지금부터 질문할게"}],
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 256,
        'temperature': 0.5,
        'repeatPenalty': 5.0,
        'stopBefore': [],
        'includeAiFilters': True
    }

    completion_executor.execute(request_data)
