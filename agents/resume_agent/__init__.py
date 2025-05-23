# agents/resume_agent/__init__.py

from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda

from agents.resume_agent import (
    compare_profiles_tool,
    structure_jd_tool,
    extract_resume_tool,
    evaluate_jd_match_tool,
    evaluate_philosophy_tool
)

def run(state: dict) -> dict:
    graph = StateGraph(dict)

    graph.add_node("compare_profiles", RunnableLambda(compare_profiles_tool.run))
    graph.add_node("structure_jd", RunnableLambda(structure_jd_tool.run))
    graph.add_node("extract_resume", RunnableLambda(extract_resume_tool.run))
    graph.add_node("evaluate_jd_match", RunnableLambda(evaluate_jd_match_tool.run))
    graph.add_node("evaluate_philosophy", RunnableLambda(evaluate_philosophy_tool.run))

    graph.set_entry_point("compare_profiles")
    graph.add_edge("compare_profiles", "structure_jd")
    graph.add_edge("structure_jd", "extract_resume")
    graph.add_edge("extract_resume", "evaluate_jd_match")
    graph.add_edge("evaluate_jd_match", "evaluate_philosophy")
    graph.set_finish_point("evaluate_philosophy")

    compiled = graph.compile()
    final_state = compiled.invoke(state)

    final_state["resume_result"] = {
        "agent": "AgentResume",
        "output": {
            "profile_comparison": final_state.get("profile_comparison", []),
            "jd_raw": final_state.get("jd_raw", ""),
            "resume_raw": final_state.get("resume_raw", []),
            "jd_alignment": final_state.get("jd_alignment", {}),
            "philosophy_alignment": final_state.get("philosophy_alignment", {})
        },
        "error": None,
        "retry": False
    }

    return final_state
