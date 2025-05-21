from graph.langgraph_runner import run_langgraph
from report.report_generator import generate_pdf

user_input = {
    "기업명": "삼성전자",
    "직무명": "소프트웨어 엔지니어",
    "사용자_스펙": {
        "학력": "서울대학교 컴퓨터공학과",
        "어학": "토익 920",
        "자격증": ["정보처리기사"],
        "인턴": "삼성 SDS 인턴",
        "수상": ["교내 해커톤 대상"]
    }
}

final_state = run_langgraph(user_input)
generate_pdf(final_state)  # ✅ PDF 생성
