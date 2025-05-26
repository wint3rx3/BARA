from agents.news_agent.news_agent_util import search_news_for_subtheme
from agents.coord_stage_1 import judge_news_relevance
import time

def search_news_by_subthemes(subthemes, keywords, company, job, already_seen, needed):
    results = []
    attempt = 0
    max_attempts = 5

    while len(results) < needed and attempt < max_attempts:
        for sub in subthemes:
            time.sleep(0.3)
            articles = search_news_for_subtheme(sub)
            if keywords:
                articles = [
                    a for a in articles
                    if any(k in a["제목"] or k in a["기사"] for k in keywords)
                ]

            for article in articles:
                title = article["제목"]
                if title in already_seen:
                    continue
                already_seen.add(title)

                if judge_news_relevance(title, article["기사"], company, job):
                    results.append(article)
                    if len(results) >= needed:
                        break
            if len(results) >= needed:
                break
        attempt += 1

    return results

def run(state: dict) -> dict:
    company_subthemes = state["기업서브테마"]
    job_subthemes = state["직무서브테마"]
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    seen_titles = set()
    cache = state.get("news_cache", {"기업": [], "직무": []})

    # ✅ 기업 기사 확보
    cached_corp = cache.get("기업", [])[:2]
    seen_titles.update(a["제목"] for a in cached_corp)
    needed_corp = max(0, 2 - len(cached_corp))
    new_corp = search_news_by_subthemes(company_subthemes, [company], company, job, seen_titles, needed_corp)
    final_corp = cached_corp + new_corp
    state["기업기사리스트"] = final_corp

    # ✅ 직무 기사 확보
    cached_job = cache.get("직무", [])[:2]
    seen_titles.update(a["제목"] for a in cached_job)
    needed_job = max(0, 2 - len(cached_job))
    new_job = search_news_by_subthemes(job_subthemes, [job], company, job, seen_titles, needed_job)
    final_job = cached_job + new_job
    state["직무기사리스트"] = final_job

    print("🔍 [search] 기업 캐시 기사 수:", len(cached_corp))
    print("🔍 [search] 기업 신규 기사 수:", len(new_corp))
    print("🔍 [search] 기업 최종 기사 수:", len(final_corp))

    print("🔍 [search] 직무 캐시 기사 수:", len(cached_job))
    print("🔍 [search] 직무 신규 기사 수:", len(new_job))
    print("🔍 [search] 직무 최종 기사 수:", len(final_job))
    return state
