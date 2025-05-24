# agents/news_agent/search_titles_tool.py

import os
import ssl
import json
import html
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
"""
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")
ssl._create_default_https_context = ssl._create_unverified_context
"""

def clean_html(raw_html: str) -> str:
    return html.unescape(urllib.parse.unquote(raw_html)).replace("<b>", "").replace("</b>", "")

"""
def search_recent_news(keyword: str) -> list:
    enc_text = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display=10"

    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    with urllib.request.urlopen(req) as response:
        if response.getcode() != 200:
            return []

        data = json.loads(response.read().decode("utf-8"))
        return [clean_html(item["title"]) for item in data.get("items", [])]
"""

def search_recent_news(keyword: str) -> list:
    # ✅ 목업 뉴스 제목 목록
    return [
        f"{keyword} 관련 최신 기술 발표",
        f"{keyword} 투자 확대 소식",
        f"{keyword} 인재 채용 강화",
        f"{keyword} AI 전략 공개",
    ]


def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    company_titles = search_recent_news(company)
    job_titles = search_recent_news(job)

    unique_titles = list(set(company_titles + job_titles))  # 중복 제거

    state["뉴스제목"] = unique_titles
    return state
