import json
from llm_client.llm import llm

def run(state: dict) -> dict:
    questions = state.get("resume_questions", [])
    values = json.dumps(state.get("company_info_result", {}).get("output", {}).get("talent", ""), ensure_ascii=False)
    vision = json.dumps(state.get("company_info_result", {}).get("output", {}).get("greeting", ""), ensure_ascii=False)

    for item in questions:
        question = item["question"]
        value_keywords = " ".join(item.get("value", []))

        prompt = f"""
당신은 자기소개서를 코칭하는 전문가입니다.

다음은 자기소개서 문항과 해당 문항에 나타난 가치(value) 키워드, 그리고 기업의 인재상/신년사입니다.

이 정보를 바탕으로, 작성자가 자기소개서를 쓸 때 기업 철학을 자연스럽게 녹여낼 수 있도록 **자연스럽고 유려한 하나의 문단**으로 작성 전략을 제시해 주세요.

출력은 반드시 **4문장 이내의 설명형 문체로 된 단일 문단**이어야 하며, 다음 사항을 반드시 지켜야 합니다:

❗ 작성 규칙:
- "1.", "2)", "①", "-", "•" 등 글머리 기호나 항목 나열 표현은 절대 사용하지 마세요
- 줄바꿈 없이 하나의 문단으로 작성하세요
- 단정적 평가 표현(예: "잘 어울립니다", "부합합니다")은 금지합니다
- 구체적인 경험을 유도하는 조언형 문체로 쓰세요

[기업 철학 정보]
- 인재상: {values}
- 신년사 요약: {vision}

[자기소개서 value 키워드]
{value_keywords}

[자기소개서 문항]
"{question}"
"""


        try:
            response = llm.chat.completions.create(
                model="solar-pro",
                messages=[{"role": "user", "content": prompt}]
            )
            item["philosophy_feedback"] = response.choices[0].message.content.strip()
        except Exception as e:
            item["philosophy_feedback"] = f"[오류 발생: {e}]"

    return state
