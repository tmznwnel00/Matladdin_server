import asyncio
from bson import json_util
from datetime import datetime
import os
import uuid
import requests
from urllib.parse import urlencode

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo

from chatbot import CompletionExecutor

load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv("MONGO_URI")
api_key = os.getenv("API_KEY")
api_key_primary_val = os.getenv("API_KEY_PRIMARY_VAL")

mongo = PyMongo(app)
CORS(app)

chatbot_dict = {}

request_data = {
    "topP": 0.8,
    "topK": 0,
    "maxTokens": 256,
    "temperature": 0.5,
    "repeatPenalty": 7.07,
    "stopBefore": [],
    "includeAiFilters": True,
}


@app.route("/")
def hello():
    return "Hello, World"


@app.route("/chat", methods=["POST"])
def create_chat():
    completion_executor = CompletionExecutor(
        host="https://clovastudio.stream.ntruss.com",
        api_key=api_key,
        api_key_primary_val=api_key_primary_val,
    )
    current_messages = [
        {"role":"system","content":"\n- 너는 유저가 마음 속으로 정한 식사 메뉴를 맞추는 챗봇이야. 질문의 답변을 통해 음식 후보군을 줄여나갈 거야.\n\n- 총 12개의 질문을 구체적인 상황 설명 및 시나리오와 함께 질문해.\n\n- 질문을 하면서 몇번째 질문인지 같이 언급해줘.\n\n- 음식 이름이 질문에 들어가면 안돼.\n\n- 유저의 답변을 토대로 마지막에 최종 메뉴를 맞추면 돼.\n\n\n- 자유 형식의 질문은 하지 마. 제시한 선택지가 무조건 있어야 해.\n\n- 예, 아니오 로 물어보면 안돼.\n\n- 선택지는 4개가 최대야.\n\n- 한번에 하나씩만 질문해.\n\n- 12가지 질문을 모두 진행해야 종료할 수 있어.\n\n\n- 아래는 너가 질문과 선택지를 말할 때의 예시야.\n###\n네번째 질문 : 더운 여름날, 땀이 비오듯 나고 있습니다. 어떤 음식을 선호하시나요?\n선택지 : 시원하고 차가운 음식 / 이열치열로 이겨낼 수 있는 뜨거운 음식\n###\n다섯번째 질문 : 스트레스를 많이 받은 날입니다. 어떤 음식으로 스트레스를 풀까요?\n선택지 : 맵고 자극적인 음식 / 달콤하고 짭짤한 음식 / 달달한 디저트 / 시원한 맥주"},
        {"role":"user","content":"메뉴 추천해줘.\n직접적인 질문이 아닌 구체적인 시나리오와 함께 질문해줘.\n선택지는 / 로 구분해서 제시해줘.\n선택지는 4개를 넘으면 안돼.\n질문은 12개를 반드시 해야해."},
        {"role":"assistant","content":"안녕하세요! 저는 여러분에게 맞는 메뉴를 추천해드리는 클로바입니다. 이제부터 저희가 준비한 질문을 드릴 건데요, 각 질문에 대해 최대한 자세히 답변해주시면 더욱 정확한 추천을 드릴 수 있습니다. 그럼 바로 시작해볼까요? \n\n첫번째 질문 : 크리스마스 기념일날, 어떤 분위기에서 식사를 하고 싶으신가요?\n선택지 : 차분하고 편안한 분위기 / 신나고 활발한 분위기\n"},
        {"role":"user","content":"차분하고 편안한 분위기"},
        {"role":"assistant","content":"차분하고 편안한 분위기에서 식사를 하고 싶으시군요!\n그럼 두번째 질문입니다.\n\n두번째 질문 : \b당신은 주말에 늦게 기상했습니다. 선호하는 식사 시간대는 언제인가요?\n선택지 : 눈 뜨자마자 이른 점심 / 잠시 휴식하고 난 오후 / 여유로운 저녁 시간 / 늦은 밤 시간의 야식"},
        {"role":"user","content":"여유로운 저녁 시간"}
    ]
    request_data["messages"] = current_messages
    execution = completion_executor.execute(request_data)

    id = uuid.uuid4()
    current_messages.append(execution["result"]["message"])
    chatbot_dict[str(id)] = current_messages
    content = execution["result"]["message"]["content"]
    
    split1 = content.split("질문 : ")[1]
    split2 = split1.split("선택지 : ")
    question = split2[0]
    
    if question[-1] == '\n':
        question = question[:-1]
    option_list = split2[1].split(" / ")
    if len(option_list) > 4:
        option_list = option_list[:4]
    
    response = {"uuid": str(id), "question": question, "option_list": option_list}
    return jsonify(response)

@app.route("/chat_completion", methods=["POST"])
def chat_completion():
    chat_id = request.args.get("uuid")
    step = request.args.get("step")
    payload = request.get_json()
    answer = payload["answer"]

    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key=api_key,
        api_key_primary_val=api_key_primary_val,
    )
    current_messages = chatbot_dict[chat_id]
    user_answer = {"role": "user", "content": answer}
    current_messages.append(user_answer)

    request_data["messages"] = current_messages
    execution = completion_executor.execute(request_data)
    print(execution["result"]["message"])
    current_messages.append(execution["result"]["message"])
    chatbot_dict[chat_id] = current_messages
        
    if step == "10":
        response = {
        "uuid": chat_id,
        "step": int(step) + 1,
        }
        return jsonify(response)
    else:
        content = execution["result"]["message"]["content"]
        split1 = content.split("질문 : ")[1]
        split2 = split1.split("선택지 : ")
        question = split2[0]
        
        if question[-1] == '\n':
            question = question[:-1]
        option_list = split2[1].split(" / ")
        if len(option_list) > 4:
            option_list = option_list[:4]
        
        response = {
            "uuid": chat_id,
            "question": question,
            "option_list": option_list,
            "step": int(step) + 1,
        }

        return jsonify(response)


def food_recommendation(chat_id):
    chat_id = request.args.get("uuid")

    completion_executor = CompletionExecutor(
        host="https://clovastudio.stream.ntruss.com",
        api_key=api_key,
        api_key_primary_val=api_key_primary_val,
    )
    current_messages = chatbot_dict[chat_id]
    user_question = {"role":"user","content":"답변을 종합해서 설명과 함께 메뉴를 제시해줘. \n메뉴는 하나만 한 단어로만 제시해줘. \n추천 메뉴는 메뉴 : 뒤에 붙여서 전달해줘.\n메뉴에 대한 설명은 줄나눔해서 아래에 덧붙여줘."}
    current_messages.append(user_question)

    request_data["messages"] = current_messages
    execution = completion_executor.execute(request_data)
    current_messages.append(execution["result"]["message"])
    response = execution["result"]["message"]["content"]
    print(execution["result"]["message"]["content"])
    
    if "메뉴: " in response:

        split1 = response.split("메뉴: ")[1]
    elif "메뉴 : " in response:
        split1 = response.split("메뉴 : ")[1]
    split2 = split1.split('\n')[0]
    if '**' in split2:
        response_food = split2.split('**')[1]
    else:
        response_food = split2
    
    response_comment = split1.split('\n')[1]
    if '설명: ' in response_comment:
        response_comment = response_comment.replace("설명: ", "")
    split3 = response.split('설명: ')
    
    
    try:
        menu = mongo.db.menu
        data = {
            "session": chat_id,
            "menu": response_food,
            "comment": response_comment,
            "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        result = menu.insert_one(data)
    except Exception as e:
        print(e)
        return jsonify({'result': 'Error', 'message': str(e)})
    return {"food": response_food, "comment": response_comment} 

def create_matbti(chat_id):
    completion_executor = CompletionExecutor(
        host="https://clovastudio.stream.ntruss.com",
        api_key=api_key,
        api_key_primary_val=api_key_primary_val,
    )
    current_messages = chatbot_dict[chat_id]
    user_question = {"role":"user","content":"그렇다면 추천해준 메뉴를 바탕으로 내 성향을 파악해줘. \n혼밥, 단체식사, 가성비, 맛있는 음식에 투자, 새로운 도전, 익숙함 중 하나를 골라줘. \n내 성향은 성향 : 뒤에 붙여서 전달해줘.\n성향에 대한 설명은 줄나눔해서 아래에 덧붙여줘."}
    current_messages.append(user_question)
    request_data["messages"] = current_messages
    execution = completion_executor.execute(request_data)

    response = execution["result"]["message"]["content"]
    print(response)
    if "성향: " in response:
        split1 = response.split("성향: ")[1]
    elif "성향 : " in response:
        split1 = response.split("성향 : ")[1]
    split2 = split1.split('\n')[0]
    if '**' in split2:
        response_matbti = split2.split('**')[1]
    else:
        response_matbti = split2
    
    response_comment = split1.split('\n')[1]
    if '설명: ' in response_comment:
        response_comment = response_comment.replace("설명: ", "")

    try:
        matbti = mongo.db.matbti
        data = {
            "session": chat_id,
            "matbti": response_matbti,
            "comment": response_comment,
            "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        result = matbti.insert_one(data)
    except Exception as e:
        print(e)
        return jsonify({'result': 'Error', 'message': str(e)})
    
    return response_matbti

@app.route("/chat", methods=["DELETE"])
def delete_chat():
    chat_id = request.args.get("uuid")
    res = food_recommendation(chat_id)
    food = res['food']
    comment = res['comment']
    matbti = create_matbti(chat_id)
    del chatbot_dict[chat_id]
    response = {
        "uuid": chat_id,
        "food": food,
        "comment": comment
    }
    return jsonify(response)


@app.route("/matbti", methods=["GET"])
def get_matbti():
    chat_id = request.args.get("uuid")

    matbti = mongo.db.matbti
    result = matbti.find_one({'session': chat_id})
    
    data = {
        "uuid": result['session'],
        "matbti": result['matbti'],
        "create_time": result["create_time"]
    }
    return jsonify(data)

@app.route("/restuarant", methods=["GET"])
def get_restuarant():
    search = request.args.get("search")
    headers = {
            'X-Naver-Client-Id': os.getenv("CLIENT_ID"),
            'X-Naver-Client-Secret': os.getenv("CLIENT_SECRET"),
          }
    query_params = {
        'query' : search,
        'display' : 3
    }

    response = requests.get('https://openapi.naver.com/v1/search/local.json', headers=headers, params=query_params)
    res = response.json()
    print(res)
    return jsonify(res['items'])

if __name__ == '__main__':
    app.run()