import json
from report_graph import build_graph
from pathlib import Path

# 1. 입력 불러오기
with open("data/sample_inputs.json", "r", encoding="utf-8") as f:
    user_input = json.load(f)

company = user_input["company"]
job = user_input["job"]
user_spec = user_input["user_spec"]

# 2. 그래프 생성
graph = build_graph()

# 3. 상태 초기화
initial_state = {
    "company": company,
    "job": job,
    "user_spec": user_spec
}

# 4. LangGraph 실행
print("📊 기업 분석 보고서를 생성 중입니다...\n")
final_state = graph.invoke(initial_state)

# 5. 결과 출력
print("✅ PDF 생성 완료!")
print(f"📁 저장 위치: {Path(final_state['pdf_path']).resolve()}")
