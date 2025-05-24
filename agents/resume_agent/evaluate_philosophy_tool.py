# agents/resume_agent/evaluate_philosophy_tool.py

import json
from llm_client.llm import llm

import json
from llm_client.llm import llm

def run(state: dict) -> dict:
    resume = state.get("resume_topics", {})
    values = json.dumps(state.get("company_info_result", {}).get("output", {}).get("talent", ""), ensure_ascii=False)
    vision = json.dumps(state.get("company_info_result", {}).get("output", {}).get("greeting", ""), ensure_ascii=False)

    result = {}

    for question_text, content in resume.items():
        question = question_text.replace("보기", "").strip()
        value = " ".join(content.get("value", []))

        prompt = f"""
당신은 자기소개서를 코칭하는 전문가입니다. 아래 정보를 참고하여, 주어진 질문에 대해 자기소개서를 어떻게 작성하면 기업 철학과 자연스럽게 연결될 수 있는지 **구체적인 작성 전략**을 제시해 주세요.

[기업 철학 정보]
- 인재상: {values}
- 신년사 요약: {vision}

[자기소개서 키워드 요약]
- {value}

[자기소개서 문항]
"{question}"

📌 작성자가 이 질문에 대해 자기소개서를 쓸 때 다음을 중심으로 조언하세요:
- 어떤 기업 철학 요소를 중심으로 녹이는 것이 효과적인지
- 어떤 경험이나 행동 예시를 활용하면 좋은지
- 문장 흐름, 구성 방식, 강조할 키워드는 어떻게 배치해야 하는지
- 평가 멘트가 아닌 **작성 전략 중심**으로 설명하세요

❗주의사항:
- "기업 철학과 부합합니다", "잘 어울립니다", "일치합니다" 같은 표현은 절대 쓰지 마세요
- 총 5문장 이내로 요약하며, 명확하고 이해하기 쉬운 문장으로 작성하세요
- 말투는 "~하는 것이 좋습니다." 형태의 조언형 서술을 유지하세요
"""

        try:
            response = llm.chat.completions.create(
                model="solar-pro",
                messages=[{"role": "user", "content": prompt}]
            )
            result[question] = response.choices[0].message.content.strip()
        except Exception as e:
            result[question] = f"[오류 발생: {e}]"

    state["philosophy_alignment"] = result
    return state
