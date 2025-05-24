from langgraph.graph import StateGraph, END
from agents import news_agent, finance_agent, resume_agent, interview_agent, coordinator_agent, company_info_agent  
from graph.state_schema import get_initial_state, State

def run_langgraph(user_input: dict, interview_data=None, interview_reviews=None) -> dict:
    state = get_initial_state(user_input)

    if interview_data is not None:
        state["interview_data"] = interview_data
    if interview_reviews is not None:
        state["interview_reviews"] = interview_reviews

    graph_builder = StateGraph(State)

    graph_builder.add_node("agent_finance", finance_agent.run)
    graph_builder.add_node("agent_news", news_agent.run)
    graph_builder.add_node("agent_resume", resume_agent.run)
    graph_builder.add_node("agent_interview", interview_agent.run)
    graph_builder.add_node("agent_coordinator", coordinator_agent.run)
    graph_builder.add_node("agent_company_info", company_info_agent.run)

    graph_builder.set_entry_point("agent_news")

    graph_builder.add_edge("agent_news", "agent_finance")         # ✅ 수정
    graph_builder.add_edge("agent_finance", "agent_company_info")
    graph_builder.add_edge("agent_company_info", "agent_resume")
    graph_builder.add_edge("agent_resume", "agent_interview")
    graph_builder.add_edge("agent_interview", "agent_coordinator")
    graph_builder.set_finish_point("agent_coordinator")

    graph_builder.set_finish_point("agent_coordinator")

    # langgraph_runner.py (run_langgraph 마지막)
    graph = graph_builder.compile()
    result = graph.invoke(state)

    return result
