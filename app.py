from flask import Flask, jsonify
from question_processing import load_data, select_best_question

app = Flask(__name__)

# 전역 변수로 모델, 임베딩, 데이터프레임을 로드
model, embedding_question, df = load_data()

# URL에서 질문을 받아 처리하는 라우트
@app.route('/get_question/<question>', methods=['GET'])
def get_question(question):
    print(question)
    question, answer, link, button_name = select_best_question(question, model, embedding_question, df)
    return jsonify({"answer": answer,
                    "button_name": button_name,
                    "link": link,
                    "question" : question})

if __name__ == '__main__':
    app.run(debug=True)
