# agents/finance_agent/__init__.py

from .get_code import run as get_code
from .fetch_data import run as fetch_data
from .chart_generator import run as generate_charts
from .analyze_insight import run as analyze_insight

def run(state: dict) -> dict:
    state = get_code(state)
    if not isinstance(state, dict):
        return {
            "finance_result": {
                "agent": "AgentFinance",
                "output": None,
                "error": "get_code가 None을 반환했습니다.",
                "retry": True
            }
        }

    if state.get("finance_result", {}).get("retry"):
        return state

    state = fetch_data(state)
    if state.get("finance_result", {}).get("retry"):
        return state

    state = generate_charts(state)
    state = analyze_insight(state)
    return state
