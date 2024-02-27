import torch
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import json
import re

# 모델과 데이터를 로드하는 함수
def load_data():
    print("데이터 로딩 중...")
    model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    embedding_question = torch.load(f"dataset/qna/24_02_27.pt")
    df = pd.read_excel(f"dataset/qna/24_02_27_embedding.xlsx")
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
            button_name = df['버튼이름'][answer]
            answer = df['답변'][answer]
        else:
            link = df['링크'][best_sim_idx]
            button_name = df['버튼이름'][best_sim_idx]
        
        if pd.isna(link):
            link = []
        else:
            link = link.strip().split('\n')
        if pd.isna(button_name):
            button_name = []
        else:
            button_name = button_name.strip().split('\n')

        if answer == "전체공지":
             with open("dataset\crawling\data_site1.json", 'r') as file:
                  answer = json.load(file)
                  combined_string = "\n".join(answer)
                  print(combined_string)
                  answer = combined_string

        elif answer == "학사일정":
             with open("dataset\crawling\data_site2.json", 'r') as file:
                answer = json.load(file)
                # Combine the strings into one, adding " end" at the end of each original string
                combined_string_with_end = " end".join(answer) + " end"
                # # \n과 \t를 제거하고 하나의 문자열로 전환하는 코드
                cleaned_string = ' '.join(combined_string_with_end.replace('\n', ' ').replace('\t', ' ').strip().split())
                # # 연속된 공백을 하나의 공백으로 축소합니다.
                text_with_reduced_spaces = '\n'.join(cleaned_string.split(' end'))
                answer = text_with_reduced_spaces

        elif answer == "도서관":
             with open("dataset\crawling\data_site3.json", 'r') as file:
                answer = json.load(file)
                # 속성들만 추출
                extracted_data = [{'ROOM_NAME': item['ROOM_NAME'], 'REMAIN_CNT': item['REMAIN_CNT'], 'USE_CNT2': item['USE_CNT2'], 'TOTAL_CNT': item['TOTAL_CNT']} for item in answer]
                room_strings = "\n".join([f"{room['ROOM_NAME']}: 총 {room['TOTAL_CNT']}석, 남은자리 {room['REMAIN_CNT']}석, 사용중 {room['USE_CNT2']}석" for room in extracted_data])
                answer = room_strings

        elif answer == "학생식당":
             with open("dataset\crawling\data_site4.json", 'r') as file:
                answer = json.load(file)
                
                # 빈 문자열을 제거한 새로운 배열 생성
                cleaned_meal_plan = [item for item in answer if item != ""]
                del cleaned_meal_plan[:4]

                # 정규표현식을 사용하여 날짜를 인식하는 패턴
                date_pattern = re.compile(r"\d{4}\.\d{2}\.\d{2}")

                # 날짜를 기준으로 하나의 문자열로 결합
                combined_schedule = ""
                current_date = None

                for item in cleaned_meal_plan:
                    if date_pattern.match(item):  # 날짜인 경우
                        if current_date:  # 이전에 날짜를 만났을 경우
                            combined_schedule += "\n"  # 이전 날짜의 정보를 마무리하고 줄바꿈 추가
                        current_date = item
                        combined_schedule += item
                    else:  # 날짜가 아닌 경우
                        combined_schedule += " " + item
                answer = combined_schedule

        return question, answer, link, button_name
