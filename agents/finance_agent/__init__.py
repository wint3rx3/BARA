# agents/finance_agent/__init__.py

from agents.finance_agent import (
    get_code,
    fetch_data,
    chart_generator,
    analyze_insight
)

def run(state: dict) -> dict:
    # ✅ 1. 코드 매핑
    state = get_code.run(state)
    if state.get("finance_result", {}).get("retry"):
        return {"finance_result": state["finance_result"]}

    # ✅ 2. 데이터 수집
    state = fetch_data.run(state)
    if state.get("finance_result", {}).get("retry"):
        return {"finance_result": state["finance_result"]}

    # ✅ 3. 차트 생성
    state = chart_generator.run(state)

    # ✅ 4. 인사이트 분석
    state = analyze_insight.run(state)

    # ✅ 5. finance_result만 추출해서 반환 (news_agent와 동일 방식)
    return {
        "finance_result": state.get("finance_result")
    }
