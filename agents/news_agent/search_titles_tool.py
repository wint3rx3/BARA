# agents/news_agent/search_titles_tool.py

from agents.news_agent.news_agent_util import search_recent_news

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    company_titles = search_recent_news(company)
    job_titles = search_recent_news(job)

    state["기업뉴스제목"] = company_titles
    state["직무뉴스제목"] = job_titles
    return state
