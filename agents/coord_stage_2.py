# agents/coord_stage_2.py

def run(state: dict) -> dict:
    error_agents = []

    # ✅ Resume 평가
    resume_result = state.get("resume_result")
    if not resume_result or resume_result.get("error") or resume_result.get("retry"):
        error_agents.append(("AgentResume", "실행 실패 또는 오류"))
    else:
        output = resume_result.get("output", {})
        if not output:
            error_agents.append(("AgentResume", "출력 없음"))
        elif not output.get("jd_alignment") or not output.get("philosophy_alignment"):
            error_agents.append(("AgentResume", "정합성 평가 결과 누락"))

    # ✅ Interview 평가
    interview_result = state.get("interview_result")
    if not interview_result or interview_result.get("error") or interview_result.get("retry"):
        error_agents.append(("AgentInterview", "실행 실패 또는 오류"))
    else:
        output = interview_result.get("output", {})
        summary = output.get("summary", {})
        qna_keys = ["potential", "communication", "competency", "personality"]

        if not summary or not any(summary.values()):
            error_agents.append(("AgentInterview", "면접 요약 없음"))

        for key in qna_keys:
            qna = output.get(key, {})
            if not qna:
                continue
            if not qna.get("question_1") or not qna.get("answer_1"):
                error_agents.append(("AgentInterview", f"{key} 질문 1 누락"))
            if not qna.get("question_2") or not qna.get("answer_2"):
                error_agents.append(("AgentInterview", f"{key} 질문 2 누락"))

    # ✅ 결과 조립
    if error_agents:
        state["coord_stage_2_result"] = {
            "agent": "CoordStage2",
            "output": {
                "status": "오류",
                "문제_에이전트": error_agents
            },
            "retry": True,
            "error": "CoordStage2 실패"
        }
    else:
        state["coord_stage_2_result"] = {
            "agent": "CoordStage2",
            "output": {
                "status": "정상",
                "문제_에이전트": []
            },
            "retry": False,
            "error": None
        }

    return state
