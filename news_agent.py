py# pip install -q langchain-core langchain langchain-community

import os
import urllib.request
import json
import re
import html
import ssl
import asyncio
from typing import List, Dict
from pydantic import BaseModel, Field
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import HumanMessage

# 네이버 API 키 설정
client_id = '**********'
client_secret = '***********'

ssl._create_default_https_context = ssl._create_unverified_context

# 최신 뉴스 제목 검색
def search_recent_news(keyword):
    encText = urllib.parse.quote(keyword)
    encText2 = urllib.parse.quote("10")
    url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&display=" + encText2
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
    else:
        print("Error Code:" + rescode)
    response_json = json.loads(response_body.decode('utf-8'))
    def clean_html(raw_html):
        no_tags = re.sub('<.*?>', '', raw_html)
        return html.unescape(no_tags)
    title_list = [clean_html(i['title']) for i in response_json.get('items', [])]
    return title_list

# OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = "***********"

# 서브 주제 생성 클래스
class NewsletterThemeOutput(BaseModel):
    theme: str = Field(description="The main newsletter theme")
    sub_themes: List[str] = Field(description="Sub themes")

# 서브 주제 생성 함수
def subtheme_generator(recent_news: List[str]):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)
    structured_llm_newsletter = llm.with_structured_output(NewsletterThemeOutput)
    system = """
    You are an expert helping to create a newsletter. Based on a list of article titles provided, your task is to choose a single,
    specific newsletter theme framed as a single keyword.
    In addition, generate 2 keywords that are highly specific, researchable news items or insights under the main theme.
    The output should be in Korean.
    """
    theme_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Article titles: \n\n {recent_news}"),
    ])
    subtheme_chain = theme_prompt | structured_llm_newsletter
    output = subtheme_chain.invoke({"recent_news": recent_news})
    return output

# 서브 주제에 대한 뉴스 검색
def search_news_for_subtheme(subtheme):
    encText = urllib.parse.quote(subtheme)
    encText2 = urllib.parse.quote("1")
    url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&display=" + encText2
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
    else:
        print("Error Code:" + rescode)
    response_json = json.loads(response_body.decode('utf-8'))
    def clean_html(raw_html):
        no_tags = re.sub('<.*?>', '', raw_html)
        return html.unescape(no_tags)
    article_info = []
    for item in response_json.get('items', []):
        article_info.append({
            '제목': clean_html(item['title']),
            '기사': clean_html(item['description']),
            '링크': item['link'],
            '날짜': item['pubDate']
        })
    return article_info

# 서브 주제별 뉴스 기사 재수집
def search_news_by_subthemes(subthemes):
    results = [search_news_for_subtheme(sub) for sub in subthemes]
    flattened_results = [res[0] for res in results if res]
    return flattened_results

# 기사 요약 생성
def write_summary_section(articles) -> Dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    summary = []
    for article in articles:
        title = article['제목']
        article_reference = f"Title: {article['제목']}\nContent: {article['기사']}\nURL : {article['링크']}..."
        prompt = f"""
        Write a summary section for the article.
        Use the following article as reference:
        <article>{article_reference}<article/>
        Summarize the key points and trends related to the article.
        Write in Korean. Add the url at the end with [링크] tag.
        """
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        summary.append({title: response.content})
    return summary

# 키워드 기준 뉴스 요약
def generate_summary_for_keyword(keyword: str) -> Dict:
    titles = search_recent_news(keyword)
    theme_info = subtheme_generator(titles)
    subthemes = theme_info.sub_themes
    articles = search_news_by_subthemes(subthemes)
    summary = write_summary_section(articles)
    return summary

# 기업 및 직무 뉴스 요약
def generate_news_summary(기업: str, 직무: str) -> Dict:
    
    comp_res = generate_summary_for_keyword(기업)
    job_res = generate_summary_for_keyword(직무)
    
    return {
        "기업": 기업,
        "기업뉴스요약": comp_res,
        "직무": 직무,
        "직무뉴스요약": job_res
    }

# 마크다운 포맷 변환 함수
def format_news_summary_as_markdown(summary_dict: Dict) -> str:
    markdown_output = []
    markdown_output.append(f"# 📌 기업 : {summary_dict['기업']}\n")
    for news in summary_dict['기업뉴스요약']:
        for title, content in news.items():
            markdown_output.append(f"### 💡 {title}\n{content}\n")
    markdown_output.append(f"\n# 📌 직무 : {summary_dict['직무']}\n")
    for news in summary_dict['직무뉴스요약']:
        for title, content in news.items():
            markdown_output.append(f"### 💡 {title}\n{content}\n")
    return "\n".join(markdown_output)

# 실행
if __name__ == "__main__":
    comp_name = input("지원하고자 하는 기업의 이름을 입력해주세요 : ")
    job_name = input("지원하고자 하는 직무를 구체적으로 입력해주세요 : ")
    
    result = generate_news_summary(comp_name, job_name)
    markdown_result = format_news_summary_as_markdown(result)
    print(markdown_result)
