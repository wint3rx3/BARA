# agents/news_agent/__init__.py

from langgraph.graph import StateGraph
from agents.news_agent import (
    search_titles_tool,
    extract_subthemes_tool,
    search_articles_tool,
    summarize_articles_tool
)

# ✅ 수정된 news_agent run 함수
def run(state: dict) -> dict:
    graph = StateGraph(dict)

    graph.add_node("search_titles", search_titles_tool.run)
    graph.add_node("extract_subthemes", extract_subthemes_tool.run)
    graph.add_node("search_articles", search_articles_tool.run)
    graph.add_node("summarize_articles", summarize_articles_tool.run)

    graph.set_entry_point("search_titles")
    graph.add_edge("search_titles", "extract_subthemes")
    graph.add_edge("extract_subthemes", "search_articles")
    graph.add_edge("search_articles", "summarize_articles")
    graph.set_finish_point("summarize_articles")

    compiled = graph.compile()
    final_state = compiled.invoke(state)

    # ✅ 핵심: 필요한 key만 추출하여 반환
    return {
        "news_result": final_state.get("news_result")
    }
