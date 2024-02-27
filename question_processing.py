import torch
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import json

# 모델과 데이터를 로드하는 함수
def load_data():
    print("데이터 로딩 중...")
    model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    embedding_question = torch.load(f"dataset/qna/23_11_05.pt")
    df = pd.read_excel(f"dataset/qna/23_11_05_embedding.xlsx")
    print("데이터 로드 완료")
    return model, embedding_question, df

# 유사한 질문을 찾는 함수
def select_best_question(question, model, embedding_question, df):
        print("질문 문장 : ",question)
        # question = question.replace(" ","")
        print("공백 제거 문장 : ", question)

        # 질문 예시 문장 인코딩 후 텐서화
        question_encode = model.encode(question)
        question_tensor = torch.tensor(question_encode)

        # 저장한 임베딩 데이터와의 코사인 유사도 측정
        cos_sim = util.cos_sim(question_tensor, embedding_question)

        # print(cos_sim)

        print(f"가장 높은 코사인 유사도 idx : {int(np.argmax(cos_sim))}")

        # 선택된 질문 출력
        best_sim_idx = int(np.argmax(cos_sim))
        selected_qes = df['질문'][best_sim_idx]
        print(f"선택된 질문 = {selected_qes}")

        # 선택된 질문 문장에 대한 인코딩
        selected_question_encode = model.encode(selected_qes)

        score = np.dot(question_tensor, selected_question_encode) / (np.linalg.norm(question_tensor) * np.linalg.norm(selected_question_encode))
        print(f"선택된 질문과의 유사도 = {score}")

        # 답변
        answer = df['답변'][best_sim_idx]

        if isinstance(answer, int):
            link = df['링크'][answer]
            button_name = df['비고'][answer]
            answer = df['답변'][answer]
        else:
            link = df['링크'][best_sim_idx]
            button_name = df['비고'][best_sim_idx]
        
        if pd.isna(link):
            link = 'No data'
        else:
            link = link.strip().split('\n')
        if pd.isna(button_name):
            button_name = 'No data'
        else:
            button_name = button_name.strip().split('\n')

        if answer == "전체공지":
             with open("dataset\crawling\data_site1.json", 'r') as file:
                  answer = json.load(file)
        elif answer == "학사일정":
             with open("dataset\crawling\data_site2.json", 'r') as file:
                  answer = json.load(file)
        elif answer == "도서관":
             with open("dataset\crawling\data_site3.json", 'r') as file:
                  answer = json.load(file)
        elif answer == "학생식당":
             with open("dataset\crawling\data_site4.json", 'r') as file:
                  answer = json.load(file)

        return question, answer, link, button_name
