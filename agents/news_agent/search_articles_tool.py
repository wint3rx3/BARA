from .news_agent_util import search_news_for_subtheme

def run(state: dict) -> dict:
    subthemes = state.get("서브테마", [])
    articles = []

    기업 = state["user_input"]["기업명"]
    직무 = state["user_input"]["직무명"]

    기업_관련 = [s for s in subthemes if 기업 in s][:2]
    직무_관련 = [s for s in subthemes if 직무 in s][:2]

    # fallback: 개수 부족 시 남은 걸로 채움
    남은 = [s for s in subthemes if s not in 기업_관련 + 직무_관련]
    while len(기업_관련) < 2 and 남은:
        기업_관련.append(남은.pop())
    while len(직무_관련) < 2 and 남은:
        직무_관련.append(남은.pop())

    for s in 기업_관련 + 직무_관련:
        res = search_news_for_subtheme(s)
        if res:
            articles.append(res[0])

    state["기사리스트"] = articles
    return state
