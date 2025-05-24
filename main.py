import pandas as pd
from graph.state_schema import get_initial_state
from graph.langgraph_runner import run_langgraph
from report.report_generator import generate_pdf

# 1. 사용자 입력 정의
user_input = {
    "기업명": "삼성전자",
    "직무명": "개발",
    "사용자_스펙": {
        "학력": "서울대학교 컴퓨터공학과",
        "어학": "토익 920",
        "자격증": ["정보처리기사"],
        "인턴": "삼성 SDS 인턴",
        "수상": ["교내 해커톤 대상"]
    }
}

# 2. 인터뷰용 데이터 준비
interview_data = pd.read_csv("data/interview_data.csv")
filtered = interview_data[
    (interview_data["기업명"] == user_input["기업명"]) &
    (interview_data["직무명"] == user_input["직무명"])
]
interview_reviews = "\n\n".join(filtered["combined_text"].dropna().tolist())

# 3. 실행 (✅ user_input만 넘김)
final_state = run_langgraph(user_input, interview_data, interview_reviews)

from pprint import pprint
print("✅ interview_result 출력:")
pprint(final_state.get("interview_result", {}).get("output", {}))

# 4. PDF 생성
generate_pdf(final_state)
