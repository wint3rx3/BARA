# agents/coord_stage_1.py

def run(state: dict) -> dict:

    error_agents = []

    # ✅ News 평가
    news_result = state.get("news_result")
    if not news_result or news_result.get("error") or news_result.get("retry"):
        error_agents.append(("AgentNews", "실행 실패 또는 오류"))
    else:
        output = news_result.get("output", {})
        articles = output.get("articles", [])
        if not articles:
            error_agents.append(("AgentNews", "뉴스 요약 비어 있음"))
        else:
            titles = [a.get("title") for a in articles if isinstance(a, dict) and "title" in a]
            if len(set(titles)) < len(titles):
                error_agents.append(("AgentNews", "중복 뉴스 제목 존재"))

    # ✅ Finance 평가
    finance_result = state.get("finance_result")
    if not finance_result or finance_result.get("error") or finance_result.get("retry"):
        error_agents.append(("AgentFinance", "실행 실패 또는 오류"))
    else:
        output = finance_result.get("output", {})
        if not output or not output.get("revenue_chart_path") or not output.get("stock_chart_path"):
            error_agents.append(("AgentFinance", "차트 경로 누락"))

    # ✅ CompanyInfo 평가
    company_info_result = state.get("company_info_result")
    if not company_info_result or company_info_result.get("error") or company_info_result.get("retry"):
        error_agents.append(("AgentCompanyInfo", "실행 실패 또는 오류"))
    else:
        output = company_info_result.get("output", {})
        if not output or not output.get("address") or not output.get("history"):
            error_agents.append(("AgentCompanyInfo", "주소 또는 연혁 정보 누락"))

    # ✅ 결과 조립
    if error_agents:
        state["coord_stage_1_result"] = {
            "agent": "CoordStage1",
            "output": {
                "status": "오류",
                "문제_에이전트": error_agents
            },
            "retry": True,
            "error": "CoordStage1 실패"
        }
    else:
        state["coord_stage_1_result"] = {
            "agent": "CoordStage1",
            "output": {
                "status": "정상",
                "문제_에이전트": []
            },
            "retry": False,
            "error": None
        }

    return state
