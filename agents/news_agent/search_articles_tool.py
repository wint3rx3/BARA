# agents/news_agent/search_articles_tool.py

import os
import ssl
import json
import html
import urllib.request
import urllib.parse
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")
ssl._create_default_https_context = ssl._create_unverified_context


def clean_html(raw_html: str) -> str:
    return html.unescape(urllib.parse.unquote(raw_html)).replace("<b>", "").replace("</b>", "")

"""
def search_news_for_keyword(keyword: str) -> List[Dict]:
    enc_text = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display=1"

    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    with urllib.request.urlopen(req) as response:
        if response.getcode() != 200:
            return []
        data = json.loads(response.read().decode("utf-8"))
        return [{
            "제목": clean_html(i["title"]),
            "기사": clean_html(i["description"]),
            "링크": i["link"],
            "날짜": i["pubDate"]
        } for i in data.get("items", [])]
"""

def search_news_for_keyword(keyword: str) -> List[Dict]:
    # ✅ API 호출 제거
    return [{
        "제목": f"{keyword} 관련 기사 제목",
        "기사": f"{keyword}와 관련된 산업 동향이 주 내용입니다.",
        "링크": "https://example.com",
        "날짜": "2024-01-01"
    }]

def run(state: dict) -> dict:
    subthemes: List[str] = state.get("서브테마", [])
    articles = []

    for keyword in subthemes:
        result = search_news_for_keyword(keyword)
        if result:
            articles.append(result[0])  # 1개만 수집

    state["기사리스트"] = articles
    return state
