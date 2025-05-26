# agents/news_agent/summarize_articles_tool.py

from llm_client.llm import llm  # ✅ Upstage API 직접 사용

def write_summary_section(articles):
    summary = []
    for article in articles:
        title = article["제목"]
        article_reference = f"Title: {article['제목']}\nContent: {article['기사']}\nURL: {article['링크']}..."

        prompt = f"""
Write a summary section for the article.

Use the following article as reference and include relevant points from its title and content:
<article>
{article_reference}
<article/>

Summarize the key points and trends related to the article. 
Keep the tone engaging and informative for the readers. You should write in Korean.

The summary should have at least 3 sentences.
Do not add the url in the summary.
"""

        response = llm.chat.completions.create(
            model="solar-pro",
            messages=[{"role": "user", "content": prompt}]
        )
        summary_text = response.choices[0].message.content.strip()
        summary.append({title: summary_text})

    return summary

# summarize_articles_tool.py

def run(state: dict) -> dict:
    company_articles = state.get("기업기사리스트", [])
    job_articles = state.get("직무기사리스트", [])

    print("📰 [summarize] 기업기사리스트:", len(company_articles))
    print("📰 [summarize] 직무기사리스트:", len(job_articles))


    # ✅ 요약 보장 조건: 기사 수 확인
    if len(company_articles) < 1 or len(job_articles) < 1:
        state["news_result"] = {
            "agent": "AgentNews",
            "output": None,
            "error": f"기사 수 부족 - 기업({len(company_articles)}/2), 직무({len(job_articles)}/2)",
            "retry": True
        }
        return state

    company_summary = write_summary_section(company_articles[:2])
    job_summary = write_summary_section(job_articles[:2])

    unified_summary = []
    for item in company_summary + job_summary:
        for title, summary in item.items():
            unified_summary.append({"title": title, "summary": summary})

    state["news_result"] = {
    "agent": "AgentNews",
    "output": {
        "기업뉴스": company_summary,
        "직무뉴스": job_summary
    },
    "error": None,
    "retry": False
}

    return state

