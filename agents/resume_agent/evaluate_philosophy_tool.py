# agents/resume_agent/evaluate_philosophy_tool.py

import json
from llm_client.llm import llm

def run(state: dict) -> dict:
    resume = state.get("resume_topics", {})
    values = json.dumps(state.get("company_info_result", {}).get("output", {}).get("talent", ""), ensure_ascii=False)
    vision = json.dumps(state.get("company_info_result", {}).get("output", {}).get("greeting", ""), ensure_ascii=False)

    result = {}

    for question_text, content in resume.items():
        value = " ".join(content.get("value", []))

        prompt = f"""
[기업 철학 정보]
신년사: {vision}
인재상: {values}

[자기소개서 기업성]
{value}

위 자기소개서의 기업성이 기업 철학과 얼마나 부합하는지 정성적으로 평가해줘.
자기소개서에서 서술한 기업성 내용을 언급하면서 반영이 된 부분만 서술해줘.
"~했다면"과 같은 말은 절대 하지 말고 실제로 기업 철학과 연결되어있는 것 같은 부분만 서술해.
"""

        try:
            response = llm.chat.completions.create(
                model="solar-pro",
                messages=[{"role": "user", "content": prompt}]
            )
            result[question_text] = response.choices[0].message.content.strip()
        except Exception as e:
            result[question_text] = f"[오류 발생: {e}]"

    state["philosophy_alignment"] = result
    return state
