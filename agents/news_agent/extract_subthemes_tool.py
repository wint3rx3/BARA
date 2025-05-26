from typing import List
from pydantic import BaseModel, Field, TypeAdapter
from llm_client.llm import llm

class NewsletterThemeOutput(BaseModel):
    theme: str = Field(description="The main newsletter theme")
    sub_themes: List[str] = Field(description="Sub themes")

json_schema = {
    "name": "newsletter_theme_output",
    "schema": {
        "type": "object",
        "properties": {
            "theme": {"type": "string"},
            "sub_themes": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["theme", "sub_themes"],
        "strict": True,
        "additionalProperties": False
    }
}

def run_llm_for_subthemes(prompt: str) -> NewsletterThemeOutput:
    response = llm.chat.completions.create(
        model="solar-pro",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_schema", "json_schema": json_schema}
    )
    return TypeAdapter(NewsletterThemeOutput).validate_json(response.choices[0].message.content)

def build_prompt(company: str, job: str, recent_titles: List[str], penalty_note: str) -> str:
    return f"""
You are an expert assisting with news summarization for job seekers. Based on the list of recent news article titles provided below, your task is to extract one specific, overarching theme framed as a single keyword.

Then, generate 2 *realistic and specific* sub-keywords under that theme. These sub-keywords must:
- Be at most 3 words long
- Be usable as Naver News search keywords
- Reflect actual trends, events, or public issues
- Be likely to appear in real-world news article titles

⚠️ Avoid academic, biomedical, or niche technical phrases unless clearly present.
⚠️ Strongly avoid political topics, elections, or government figures.
⚠️ One keyword must include "{company}", one must include "{job}" (in Korean).

{penalty_note}

뉴스 제목 리스트:
{chr(10).join(recent_titles)}
"""

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    company_titles = state["기업뉴스제목"]
    job_titles = state["직무뉴스제목"]

    feedback = state.get("news_feedback_history", [])
    irrelevant = {t for fb in feedback for t in fb.get("irrelevant_titles", [])}
    duplicates = {tuple(p) for fb in feedback for p in fb.get("duplicate_pairs", [])}

    penalty_lines = []
    if irrelevant:
        penalty_lines.append("다음 뉴스 제목들은 관련 없음으로 판단됨. 유사 주제 피해주세요:")
        penalty_lines.extend(f"- {t}" for t in sorted(irrelevant))
    if duplicates:
        penalty_lines.append("다음 뉴스 쌍은 중복된 내용으로 판단됨. 유사 주제 피해주세요:")
        penalty_lines.extend(f"- \"{t1}\" / \"{t2}\"" for t1, t2 in sorted(duplicates))

    penalty_note = "\n".join(penalty_lines)

    company_output = run_llm_for_subthemes(build_prompt(company, job, company_titles, penalty_note))
    job_output = run_llm_for_subthemes(build_prompt(company, job, job_titles, penalty_note))

    print("🧵 생성된 기업 서브테마:", company_output.sub_themes)
    print("🧵 생성된 직무 서브테마:", job_output.sub_themes)

    state["기업서브테마"] = company_output.sub_themes
    state["직무서브테마"] = job_output.sub_themes
    return state
