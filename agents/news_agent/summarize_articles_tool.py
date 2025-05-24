# agents/news_agent/summarize_articles_tool.py

from typing import List, Dict
from llm_client.llm import llm
from difflib import SequenceMatcher

def is_similar(title1: str, title2: str, threshold: float = 0.85) -> bool:
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio() >= threshold

def summarize_article(title: str, content: str, link: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "너는 기사 요약 전문가야. 내용을 100~300자 사이로 요약하고 링크를 포함해줘."
        },
        {
            "role": "user",
            "content": f"제목: {title}\n\n내용: {content}\n\n링크: {link}"
        }
    ]

    try:
        response = llm.chat.completions.create(
            model="solar-pro",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[요약 실패: {e}]"

def run(state: dict) -> dict:

    articles: List[Dict] = state.get("기사리스트", [])
    seen_titles = []
    summaries = []

    for article in articles:
        title = article["제목"]
        if any(is_similar(title, seen) for seen in seen_titles):
            continue
        seen_titles.append(title)

        summary_text = summarize_article(title, article["기사"], article["링크"])
        if 100 <= len(summary_text) <= 500:
            summaries.append({
                "title": title,
                "summary": summary_text,
                "link": article["링크"]
            })

    # ✅ 요약 실패했더라도 반드시 news_result 설정
    if summaries:
        state["news_result"] = {
            "agent": "AgentNews",
            "output": {
                "articles": summaries
            },
            "error": None,
            "retry": False
        }
    else:
        state["news_result"] = {
            "agent": "AgentNews",
            "output": {
                "articles": []
            },
            "error": "요약된 뉴스가 없습니다.",
            "retry": True  # ✅ 다시 실행될 수 있도록
        }
    print("📤 요약 완료, news_result에 저장됨")
    return state

