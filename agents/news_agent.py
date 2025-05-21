# agents/news_agent.py

import os
import re
import html
import json
import ssl
import urllib.request
import urllib.parse
import asyncio
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import HumanMessage
from difflib import SequenceMatcher
from agents._shared.llm import default_llm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from dotenv import load_dotenv

# ✅ 환경 변수 로딩 (.env 필요)
load_dotenv()
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

ssl._create_default_https_context = ssl._create_unverified_context

# 🔹 뉴스 테마 출력 스키마
class NewsletterThemeOutput(BaseModel):
    theme: str = Field(description="뉴스레터 메인 주제")
    sub_themes: List[str] = Field(description="세부 주제들")

# 🔹 HTML 제거
def clean_html(raw_html: str) -> str:
    no_tags = re.sub("<.*?>", "", raw_html)
    return html.unescape(no_tags)

# 🔹 뉴스 제목 검색
def search_recent_news(keyword: str) -> List[str]:
    encText = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display=10"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)
    with urllib.request.urlopen(req) as response:
        if response.getcode() != 200:
            raise RuntimeError(f"Naver API Error {response.getcode()}")
        data = json.loads(response.read().decode("utf-8"))
        return [clean_html(item["title"]) for item in data.get("items", [])]

# 🔹 서브 키워드 생성
subtheme_prompt = PromptTemplate(
    input_variables=["recent_news"],
    template="""
다음 뉴스 제목들을 참고하여 핵심 주제 1개와 세부 주제 2개를 한국어로 JSON 형태로 추출하세요.

뉴스 제목 목록:
{recent_news}

예시 출력:
{
  "theme": "반도체 산업 경쟁 심화",
  "sub_themes": ["삼성의 HBM 투자", "TSMC와의 기술 경쟁"]
}
"""
)
structured_llm = default_llm.with_structured_output(NewsletterThemeOutput)
subtheme_chain = LLMChain(llm=structured_llm, prompt=subtheme_prompt)

def subtheme_generator(news_titles: List[str]) -> NewsletterThemeOutput:
    return subtheme_chain.run({"recent_news": "\n".join(news_titles)})

# 🔹 세부 주제로 뉴스 기사 검색
def search_news_for_subtheme(subtheme: str) -> List[Dict]:
    encText = urllib.parse.quote(subtheme)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display=1"
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

# 🔹 뉴스 기사 요약
def is_similar(title1: str, title2: str, threshold: float = 0.85) -> bool:
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio() >= threshold

def summarize_articles(articles: List[Dict]) -> List[Dict[str, str]]:
    summaries = []
    seen_titles = []

    for article in articles:
        title = article["제목"]
        if any(is_similar(title, seen) for seen in seen_titles):
            continue
        seen_titles.append(title)

        prompt = f"""기사 제목: {title}\n내용: {article['기사']}\n
한국어로 핵심 내용을 요약하고, 마지막에 [링크]를 포함하세요.\n{article['링크']}"""
        
        result = default_llm.invoke([HumanMessage(content=prompt)])
        summary_text = result.content.strip()

        if 100 <= len(summary_text) <= 500:
            summaries.append({
                "제목": title,
                "요약": summary_text
            })

    return summaries

# 🔹 하나의 키워드에 대한 뉴스 요약
async def generate_summary_for_keyword(keyword: str) -> List[Dict[str, str]]:
    titles = search_recent_news(keyword)
    theme_info = subtheme_generator(titles)
    articles = []
    seen_titles = []

    for sub in theme_info.sub_themes:
        result = search_news_for_subtheme(sub)
        for article in result:
            title = article["제목"]
            if any(is_similar(title, seen) for seen in seen_titles):
                continue
            seen_titles.append(title)
            articles.append(article)
            break  # 한 subtheme당 1개만

    return summarize_articles(articles)

# 🔹 기업 + 직무 뉴스 요약 (병렬 실행)
async def generate_news_summary(기업: str, 직무: str) -> Dict:
    기업_task = generate_summary_for_keyword(기업)
    직무_task = generate_summary_for_keyword(직무)
    기업요약, 직무요약 = await asyncio.gather(기업_task, 직무_task)
    return {
    "뉴스": 기업요약 + 직무요약  # 두 리스트를 합침
}

"""
# 🔹 LangGraph 노드용 에이전트 진입점
def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    try:
        result = asyncio.run(generate_news_summary(company, job))
        state["news_result"] = {
            "agent": "AgentNews",
            "output": result,  # JSON 구조
            "error": None,
            "retry": False
        }
    except Exception as e:
        state["news_result"] = {
            "agent": "AgentNews",
            "output": None,
            "error": str(e),
            "retry": True
        }

    return state"""

def run(state: dict) -> dict:
    state["news_result"] = {
        "agent": "AgentNews",
        "output": {
            "뉴스": [
                {"제목": "삼성전자, 반도체 투자 확대", "요약": "삼성전자가 차세대 HBM 생산에 박차를 가하고 있습니다. [링크]"},
                {"제목": "AI 인재 확보 경쟁", "요약": "삼성전자는 AI 분야 인재 영입을 가속화하고 있습니다. [링크]"}
            ]
        },
        "error": None,
        "retry": False
    }
    return state
