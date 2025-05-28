from typing import List
from pydantic import BaseModel, Field, TypeAdapter
from llm_client.llm import llm
import re

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

def extract_keywords(title: str) -> List[str]:
    return [w for w in re.findall(r"[가-힣A-Za-z0-9]{2,}", title) if len(w) >= 2]

def build_prompt(company: str, job: str, recent_titles: List[str], penalty_note: str, block_keywords: List[str]) -> str:
    block_list = "\n".join(f"- {kw}" for kw in block_keywords) if block_keywords else "없음"
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

🚫 The following keywords or phrases are known to cause irrelevant or duplicate articles. Avoid using them:
{block_list}

뉴스 제목 리스트:
{chr(10).join(recent_titles)}
"""

# ✅ 핵심 보완 로직: 중복된 서브테마 재생성 차단
def rerun_until_distinct(themes_func, past_subthemes: List[str], max_attempts=3):
    attempt = 0
    while attempt < max_attempts:
        result = themes_func()
        new_subthemes = result.sub_themes
        if not any(sub in past_subthemes for sub in new_subthemes):
            return result
        attempt += 1
        print(f"⚠️ 유사한 서브테마 감지됨, 재시도 {attempt}회")
    return result

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

    blocked_keywords = set()
    for t1, t2 in duplicates:
        blocked_keywords.update(extract_keywords(t1))
        blocked_keywords.update(extract_keywords(t2))

    company_prompt = build_prompt(company, job, company_titles, penalty_note, list(blocked_keywords))
    job_prompt = build_prompt(company, job, job_titles, penalty_note, list(blocked_keywords))

    company_output = rerun_until_distinct(
        lambda: run_llm_for_subthemes(company_prompt),
        state.get("기업서브테마", [])
    )
    job_output = rerun_until_distinct(
        lambda: run_llm_for_subthemes(job_prompt),
        state.get("직무서브테마", [])
    )

    state["기업서브테마"] = company_output.sub_themes
    state["직무서브테마"] = job_output.sub_themes
    return state
