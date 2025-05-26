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
당신은 합격자 자기소개서를 분석해, 취업준비생에게 어떤 방식으로 자기소개서를 작성하면 좋을지 전략을 제시하는 전문가입니다.

아래는 해당 직무의 요구사항(직무 설명 요약)과, 실제 합격자 자기소개서에서 추출한 태도와 경험 키워드입니다.

이 자료를 바탕으로, 해당 질문에 대해 **합격자들은 어떤 경험을 바탕으로, 어떤 흐름으로 자소서를 작성했는지 요약하고**, 이를 기반으로 **취업준비생이 어떤 전략으로 접근하면 좋은지** 설명해 주세요.

[직무 설명 요약]
{jd_summary}

[합격자 자소서 키워드 요약]
- 태도: {attitude}
- 유관경험: {experience}

[자기소개서 문항]
"{question}"

📌 아래 내용을 포함해야 합니다:
- 실제 합격자들이 어떤 경험을 바탕으로 답변했는지 요약
- 해당 문항에서 자주 활용된 직무 요구사항(역량) 중심으로 설명
- 어떤 문단 흐름(예: 목표 설정 → 장애물 → 극복 → 성과)이 적절한지 안내
- 취업준비생이 참고할 수 있는 문장 스타일이나 키워드 예시 포함

❗주의사항:
- "잘 맞는다", "부합한다" 같은 평가는 하지 마세요.
- 말투는 "~하는 방식이 자주 사용됩니다.", "~하는 전략이 효과적입니다."처럼 설명형으로 작성하세요.
- 총 5~7문장 이내로 간결하게 작성하세요.
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
