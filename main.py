import pandas as pd
from graph.state_schema import get_initial_state
from graph.langgraph_runner import run_langgraph
from report.report_generator import generate_pdf

# 1. 사용자 입력 정의
user_input = {
    "기업명": "현대자동차",
    "직무명": "엔지니어링",
    "사용자_스펙": {
        "학점": "3.8/4.5",
        "어학": "토익 920",
        "자격증": 2,
        "인턴": 1,
        "수상": 1,
        "동아리": 3
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

# 4. PDF 생성
generate_pdf(final_state)
