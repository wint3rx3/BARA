# agents/resume_agent/evaluate_jd_match_tool.py

import json
from llm_client.llm import llm

def run(state: dict) -> dict:
    jd = state.get("jd_structured", {})
    resume = state.get("resume_topics", {})
    result = {}

    jd_summary = json.dumps(jd, ensure_ascii=False)

    for question, content in resume.items():
        attitude = ", ".join(content.get("attitude", []))
        experience = ", ".join(content.get("experience", []))

        prompt = f"""
[JD 요약 정보]
{jd_summary}

[자기소개서 요약 정보]
- 태도: {attitude}
- 유관경험: {experience}

자기소개서에 나타난 태도 및 경험이 JD의 필요역량/주요업무와 얼마나 부합하는지 평가하고, 자연어 문장으로 구체적으로 서술해줘.
태도와 유관경험에 대한 내용을 서술할 필요는 없고, JD의 내용이 자기소개서에 얼마나 드러나있는지만 서술해.
두 데이터의 말이 똑같을 필요는 없어. JD에서 언급된 추상적인 개념이 자기소개서에 구체적인 경험 및 태도로 서술되어있으면 돼.
"""

        try:
            response = llm.chat.completions.create(
                model="solar-pro",
                messages=[{"role": "user", "content": prompt}]
            )
            result[question] = response.choices[0].message.content.strip()
        except Exception as e:
            result[question] = f"[오류 발생: {e}]"

    state["jd_alignment"] = result
    return state
