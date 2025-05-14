from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from agent1_news import run_agent1
from agent2_finance import run_agent2
from agent3_interview import run_agent3

from models import Agent1Output, Agent2Output, Agent3Output
from report_builder import render_report, save_markdown_and_pdf


# 1. 상태 정의
class ReportState(TypedDict):
    company: str
    job: str
    user_spec: dict

    agent1: Agent1Output
    agent2: Agent2Output
    agent3: Agent3Output

    markdown: str
    pdf_path: str


# 2. 각 노드 정의
def run_agent1_node(state: ReportState):
    return {"agent1": run_agent1(state["company"], state["job"])}

def run_agent2_node(state: ReportState):
    return {"agent2": run_agent2(state["company"])}

def run_agent3_node(state: ReportState):
    return {"agent3": run_agent3(state["company"], state["job"], state["user_spec"])}

def combine_and_render(state: ReportState):
    markdown = render_report(state["agent1"], state["agent2"], state["agent3"])
    pdf_path = save_markdown_and_pdf(markdown)
    return {
        "markdown": markdown,
        "pdf_path": pdf_path
    }

# 3. 그래프 구성
def build_graph():
    workflow = StateGraph(ReportState)

    # 노드 이름을 *_node로 변경
    workflow.add_node("agent1_node", run_agent1_node)
    workflow.add_node("agent2_node", run_agent2_node)
    workflow.add_node("agent3_node", run_agent3_node)
    workflow.add_node("combine_node", combine_and_render)

    # 연결도 동일하게 반영
    workflow.add_edge(START, "agent1_node")
    workflow.add_edge("agent1_node", "agent2_node")
    workflow.add_edge("agent2_node", "agent3_node")
    workflow.add_edge("agent3_node", "combine_node")
    workflow.add_edge("combine_node", END)

    return workflow.compile()
