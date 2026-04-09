import os
import json
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
from tools import evaluate_semantic_similarity, verify_data_accuracy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '../.env'))

class XanhSMEvalAgent:
    def __init__(self):
        self.results = []
        self.backend_url = "http://127.0.0.1:8000/chat" # thay bằng url backend api của nhóm

    def call_bot_api(self, question):
        """Gọi API thực tế từ Backend (Thay đổi khi chạy thật)"""
        try:
            return requests.post(self.backend_url, json={"query": question}).json()['answer']
            # return "Có, tài xế có quyền từ chối nếu hành lý cồng kềnh gây mất an toàn theo mục 3.3."
        except:
            return "Error: Connection failed"

    def run_suite(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            cases = json.load(f)

        for case in cases:
            # Đọc đúng các trường từ mẫu JSON của bạn
            tc_id = case.get('id', 'N/A')
            category = case.get('category', 'General')
            q = case['question']
            expected = case['expected_answer']
            source = case.get('source', 'Unknown')
            
            actual = self.call_bot_api(q)

            # --- LOGIC GỌI TOOL PHÂN TẦNG ---
            fact_result = verify_data_accuracy(actual, expected)
            is_fact_ok = fact_result['numbers_match']

            # Chỉ gọi AI check ngữ nghĩa nếu số liệu đã khớp
            if is_fact_ok:
                sim_result = evaluate_semantic_similarity(actual, expected)
                score = sim_result['score']
                verdict = sim_result['verdict']
            else:
                score = 0.0
                verdict = "FAIL"

            self.results.append({
                "ID": tc_id,
                "Category": category,
                "Question": q,
                "Bot_Reply": actual,
                "Similarity_Score": score,
                "Status": "SUCCESS" if (is_fact_ok and verdict == "PASS") else "FAILED",
                "Source_Ref": source
            })
            print(f"[{tc_id}] {category} -> Score: {score}%")

    def export(self):
        df = pd.DataFrame(self.results)
        log_path = os.path.join(BASE_DIR, f"../test_cases/logs/report_{datetime.now().strftime('%m%d_%H%M')}.csv")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        df.to_csv(log_path, index=False, encoding='utf-8-sig')
        print(f"✅ Báo cáo đã xuất: {log_path}")

if __name__ == "__main__":
    agent = XanhSMEvalAgent()
    agent.run_suite(os.path.join(BASE_DIR, "../golden_datasets/ground_truth.json"))
    agent.export()