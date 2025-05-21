# agents/coordinator_agent.py

def run(state: dict) -> dict:
    error_agents = []

    # ✅ NEWS 평가
    news_result = state.get("news_result")
    if not news_result or news_result.get("error") or news_result.get("retry"):
        error_agents.append(("AgentNews", "실행 실패 또는 오류"))
    else:
        news_output = news_result.get("output", {})
        뉴스목록 = news_output.get("뉴스", [])

        if not 뉴스목록:
            error_agents.append(("AgentNews", "뉴스 목록 비어 있음"))

        # 중복 제목 검사
        titles = [item["제목"] for item in 뉴스목록 if isinstance(item, dict) and "제목" in item]
        if len(set(titles)) < len(titles):
            error_agents.append(("AgentNews", "중복 기사 제목 존재"))

    # ✅ INTERVIEW 평가
    interview_result = state.get("interview_result")
    if not interview_result or interview_result.get("error") or interview_result.get("retry"):
        error_agents.append(("AgentInterview", "실행 실패 또는 오류"))
    else:
        interview_output = interview_result.get("output", {})
        summary = interview_output.get("summary", {})
        soft = interview_output.get("인성 질문", {})
        hard = interview_output.get("직무 질문", {})

        if not summary or not any(summary.values()):
            error_agents.append(("AgentInterview", "면접 요약 비어 있음"))

        for cat_name, qna in [("인성", soft), ("직무", hard)]:
            if not qna.get("question_1") or not qna.get("answer_1"):
                error_agents.append(("AgentInterview", f"{cat_name} 질문 1 누락"))
            if not qna.get("question_2") or not qna.get("answer_2"):
                error_agents.append(("AgentInterview", f"{cat_name} 질문 2 누락"))

    # ✅ 결과 조립
    if error_agents:
        coord_output = {
            "상태": "오류",
            "문제_에이전트": error_agents,
            "재실행_필요": True
        }
    else:
        coord_output = {
            "상태": "정상",
            "문제_에이전트": [],
            "재실행_필요": False
        }

    state["coord_result"] = {
        "agent": "AgentCoordinator",
        "output": coord_output,
        "error": None,
        "retry": False
    }

    return state