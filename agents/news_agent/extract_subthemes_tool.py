# agents/news_agent/extract_subthemes_tool.py

from typing import List
from pydantic import BaseModel, Field, TypeAdapter
from llm_client.llm import llm  # ✅ Upstage API 직접 사용

class NewsletterThemeOutput(BaseModel):
    theme: str = Field(description="The main newsletter theme")
    sub_themes: List[str] = Field(description="Sub themes")

json_schema = {
    "name": "newsletter_theme_output",
    "schema": {  # ✅ 'schema' 키 아래에 구조를 중첩해야 함
        "type": "object",
        "properties": {
            "theme": {
                "type": "string",
                "description": "The main newsletter theme"
            },
            "sub_themes": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Sub themes"
            }
        },
        "required": ["theme", "sub_themes"],
        "strict": True,
        "additionalProperties": False
    }
}

def build_prompt(company: str, job: str, recent_titles: List[str], penalty_note: str) -> str:
    return f"""
You are an expert assisting with news summarization for job seekers. Based on the list of recent news article titles provided below, your task is to extract one specific, overarching theme framed as a single keyword.

Then, generate 2 *realistic and specific* sub-keywords under that theme. These sub-keywords must:
- Be at most 3 words long
- Be usable as Naver News search keywords
- Reflect actual trends, events, or public issues
- Be likely to appear in real-world news article titles

⚠️ Do not generate abstract academic or biomedical phrases unless they appear in the titles.
⚠️ Avoid keywords that are too technical, niche, or unrelated to business/employment topics.
⚠️ Strongly avoid political topics, politicians, elections, or anything related to government policy or political discourse.
⚠️ Ensure one keyword includes the company name "{company}" and one includes the job name "{job}", naturally in Korean.

{penalty_note}

All output must be written in Korean.

뉴스 제목 리스트:
{chr(10).join(recent_titles)}
"""



def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    company_titles = state["기업뉴스제목"]
    job_titles = state["직무뉴스제목"]

    # 🔍 누적 피드백 반영
    feedback_history = state.get("news_feedback_history", [])
    all_irrelevant = set()
    all_duplicates = set()
    for fb in feedback_history:
        all_irrelevant.update(fb.get("irrelevant_titles", []))
        all_duplicates.update(tuple(pair) for pair in fb.get("duplicate_pairs", []))

    penalty_lines = []
    if all_irrelevant:
        penalty_lines.append("다음 뉴스 제목들은 관련이 없다고 판단되었습니다. 유사 주제를 피해주세요:")
        penalty_lines.extend(f"- {t}" for t in sorted(all_irrelevant))
    if all_duplicates:
        penalty_lines.append("\n다음 뉴스 쌍은 중복된 내용으로 판단되었습니다. 유사한 주제를 피해주세요:")
        penalty_lines.extend(f"- \"{t1}\" / \"{t2}\"" for t1, t2 in sorted(all_duplicates))
    penalty_note = "\n".join(penalty_lines)

    # ✅ 프롬프트 실행
    company_prompt = build_prompt(company, job, company_titles, penalty_note)
    job_prompt = build_prompt(company, job, job_titles, penalty_note)

    company_output = run_llm_for_subthemes(company_prompt)
    job_output = run_llm_for_subthemes(job_prompt)

    # ✅ 콘솔 출력 추가
    print("🧵 생성된 기업 서브테마:", company_output.sub_themes)
    print("🧵 생성된 직무 서브테마:", job_output.sub_themes)

    # ✅ 결과 저장
    state["기업서브테마"] = company_output.sub_themes
    state["직무서브테마"] = job_output.sub_themes
    return state
