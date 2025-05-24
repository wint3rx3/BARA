from agents.interview_agent.summarize_tool import summarize
from agents.interview_agent.qna_tool import generate_qna

def run(state: dict) -> dict:
    # 1. 면접 요약 수행
    state = summarize(state)
    if state.get("interview_result", {}).get("retry"):
        return {
            "interview_result": state["interview_result"]
        }

    # 2. 예상 질문/답변 생성
    state = generate_qna(state)

    # ✅ 최종 결과만 반환
    return {
        "interview_result": state["interview_result"]
    }
