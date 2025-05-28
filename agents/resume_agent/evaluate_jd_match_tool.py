import json
from llm_client.llm import llm

def run(state: dict) -> dict:
    jd = state.get("jd_structured", {})
    questions = state.get("resume_questions", [])

    jd_summary = json.dumps(jd, ensure_ascii=False)

    for item in questions:
        question = item["question"]
        attitude = ", ".join(item.get("attitude", []))
        experience = ", ".join(item.get("experience", []))

        prompt = f"""
당신은 합격자 자기소개서를 분석해, 취업준비생에게 자소서를 어떻게 작성하면 좋을지 전략을 제시하는 전문가입니다.

아래는 해당 직무의 채용공고 요약과, 실제 자소서에서 추출된 태도 및 유관경험입니다.

채용공고 기반의 작성 전략을 최대 4문장 이내로 자연스럽고 간결하게 제시해 주세요.

❗ 작성 규칙:
- 반드시 하나의 문단으로 작성하세요 (줄바꿈 없이 이어지는 설명형 문장)
- 숫자나 기호(예: 1., 2), ①, ②, -, • 등 글머리표는 절대 사용하지 마세요
- 항목 나열 대신 조언 중심의 설명형 문체로 쓰세요
- 구체적인 키워드나 경험 예시는 자연스럽게 녹여내세요

[채용공고 요약]
{jd_summary}

[자기소개서 요약]
- 태도: {attitude}
- 유관경험: {experience}

[자기소개서 문항]
"{question}"
"""

        try:
            response = llm.chat.completions.create(
                model="solar-pro",
                messages=[{"role": "user", "content": prompt}]
            )
            item["jd_feedback"] = response.choices[0].message.content.strip()
        except Exception as e:
            item["jd_feedback"] = f"[오류 발생: {e}]"

    return state
