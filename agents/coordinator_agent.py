def run(state: dict) -> dict:
    required_fields = [
        "company_info_result", "news_result", "finance_result",
        "resume_result", "interview_result"
    ]

    missing = [key for key in required_fields if not state.get(key) or state[key].get("error")]

    if missing:
        state["coord_result"] = {
            "agent": "AgentCoordinator",
            "output": {"상태": "실패", "누락": missing},
            "retry": True,
            "error": f"최종 누락 필드: {missing}"
        }
    else:
        state["coord_result"] = {
            "agent": "AgentCoordinator",
            "output": {"상태": "성공"},
            "retry": False,
            "error": None
        }

    return state
