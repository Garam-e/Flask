# 파이썬 라이브러리
import json
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

# 모듈
from question_processing import load_data, select_best_question
from crawler import *

app = Flask(__name__)
scheduler = BackgroundScheduler()

# 사이트 1 크롤링 및 저장
def crawl_site1():
    data = crawl_notices()
    print(1)
    with open('dataset\crawling\data_site1.json', 'w') as file:
        json.dump(data, file)

# 사이트 2 크롤링 및 저장
def crawl_site2():
    data = crawl_academic_schedule()
    print(2)
    with open('dataset\crawling\data_site2.json', 'w') as file:
        json.dump(data, file)

# 사이트 3 크롤링 및 저장
def crawl_site3():
    data = crawl_library_seats()
    data = json.loads(data)
    print(3)
    with open('dataset\crawling\data_site3.json', 'w') as file:
        json.dump(data['body']['SectorUsingList'], file)

# 사이트 4 크롤링 및 저장
def crawl_site4():
    data = crawl_cafeteria_menu()
    print(4)
    with open('dataset\crawling\data_site4.json', 'w') as file:
        json.dump(data, file)

# 스케줄러에 작업 추가
## 전체 공지: 1시간, 학사일정: 1일, 
## 도서관 좌석: 10초, 학식 메뉴: 1주일(월)
scheduler.add_job(crawl_site1, 'interval', hours=1)
scheduler.add_job(crawl_site2, 'interval', days=1)
scheduler.add_job(crawl_site3, 'interval', seconds=10)
scheduler.add_job(crawl_site4, 'interval', weeks=1, start_date='2024-01-22')
scheduler.start()

@app.route('/')
def hello_world():
    return 'Hello, World!'

# 전역 변수로 모델, 임베딩, 데이터프레임을 로드
model, embedding_question, df = load_data()

# URL에서 질문을 받아 처리하는 라우트
@app.route('/get-question/<question>', methods=['GET'])
def get_question(question):
    print(question)
    question, answer, link, button_name = select_best_question(question, model, embedding_question, df)
    return jsonify({"answer": answer,
                    "button_name": button_name,
                    "link": link,
                    "question" : question})

# # 데이터를 반환하는 라우트
# @app.route('/get-data/<site>')
# def get_data(site):
#     filename = f'dataset\crawling\data_site{site}.json'
#     try:
#         with open(filename, 'r') as file:
#             data = json.load(file)
#         return jsonify(data)
#     except FileNotFoundError:
#         return jsonify({"error": "Data not found"}), 404
    
if __name__ == '__main__':
    # app.debug = True # 깃에 올릴때는 지우기
    # 서버 시작 시 크롤링 바로 실행
    crawl_site1()
    crawl_site2()
    crawl_site3()
    crawl_site4()
    app.run(host='0.0.0.0', port=5000)
