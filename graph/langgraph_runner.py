from langgraph.graph import StateGraph
from agents import (
    news_agent, finance_agent, resume_agent, interview_agent,
    coordinator_agent, company_info_agent, coord_stage_1, coord_stage_2
)
from graph.state_schema import get_initial_state, State

# ✅ 각 에이전트 실행 래퍼 - user_input 제거
def run_news_agent(state):
    updated = news_agent.run(state)
    print("🧪 run_news_agent 반환 키:", list(updated.keys()))
    #updated.pop("user_input", None)
    state.update(updated)
    return state

def run_news_agent_with_retry(state):
    retry_count = 0
    while True:
        state = run_news_agent(state)
        coord = coord_stage_1.run(state)
        state.update(coord)

        retry = coord.get("coord_stage_1_result", {}).get("retry", False)
        if not retry:
            break

        retry_count += 1
        print(f"🔁 AgentNews 재시도: {retry_count}회")

    return state

def run_company_info_agent(state):
    updated = company_info_agent.run(state)
    print("🧪 run_company_info_agent 반환 키:", list(updated.keys()))
    updated.pop("user_input", None)
    state.update(updated)
    return state

def run_finance_agent(state):
    updated = finance_agent.run(state)
    print("🧪 run_finance_agent 반환 키:", list(updated.keys()))
    updated.pop("user_input", None)
    state.update(updated)
    return state

def run_resume_agent(state):
    updated = resume_agent.run(state)
    print("🧪 run_resume_agent 반환 키:", list(updated.keys()))
    updated.pop("user_input", None)
    state.update(updated)
    return state

def run_interview_agent(state):
    updated = interview_agent.run(state)
    print("🧪 run_interview_agent 반환 키:", list(updated.keys()))
    updated.pop("user_input", None)
    state.update(updated)
    return state

# ✅ 전체 LangGraph 실행 함수
def run_langgraph(user_input: dict, interview_data=None, interview_reviews=None) -> dict:
    state = get_initial_state(user_input)
    if interview_data is not None:
        state["interview_data"] = interview_data
    if interview_reviews is not None:
        state["interview_reviews"] = interview_reviews

    builder = StateGraph(State)

    # 시작점
    builder.add_node("start", lambda s: s)
    builder.set_entry_point("start")

    # 순차 실행 노드 추가
    builder.add_node("agent_news", run_news_agent_with_retry)
    builder.add_edge("start", "agent_news")

    builder.add_node("agent_company_info", run_company_info_agent)
    builder.add_edge("agent_news", "agent_company_info")

    builder.add_node("agent_finance", run_finance_agent)
    builder.add_edge("agent_company_info", "agent_finance")

    builder.add_node("coord_stage_1", coord_stage_1.run)
    builder.add_edge("agent_finance", "coord_stage_1")

    builder.add_node("agent_resume", run_resume_agent)
    builder.add_edge("coord_stage_1", "agent_resume")

    builder.add_node("agent_interview", run_interview_agent)
    builder.add_edge("agent_resume", "agent_interview")

    builder.add_node("coord_stage_2", coord_stage_2.run)
    builder.add_edge("agent_interview", "coord_stage_2")

    builder.add_node("agent_coordinator", coordinator_agent.run)
    builder.add_edge("coord_stage_2", "agent_coordinator")

    # 종료점 설정
    builder.set_finish_point("agent_coordinator")

    # 실행
    graph = builder.compile()
    return graph.invoke(state)
