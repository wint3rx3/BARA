def run(state: dict) -> dict:
    from .news_agent_util import search_recent_news
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    titles = list(set(search_recent_news(company) + search_recent_news(job)))
    state["뉴스제목"] = titles
    return state
