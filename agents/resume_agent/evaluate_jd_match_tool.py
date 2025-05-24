import json
from llm_client.llm import llm

def run(state: dict) -> dict:
    jd = state.get("jd_structured", {})
    resume = state.get("resume_topics", {})
    result = {}

    jd_summary = json.dumps(jd, ensure_ascii=False)

    for question_raw, content in resume.items():
        question = question_raw.replace("보기", "").strip()
        attitude = ", ".join(content.get("attitude", []))
        experience = ", ".join(content.get("experience", []))

        prompt = f"""
당신은 자기소개서 첨삭 전문가입니다.

아래의 JD 요약과 자기소개서 요약을 참고하여, 사용자가 다음 질문에 답할 때 어떤 내용과 경험을 쓰는 것이 좋은지 구체적으로 조언해 주세요.

[JD 요약 정보]
{jd_summary}

[자기소개서 요약 키워드]
- 태도: {attitude}
- 유관경험: {experience}

[자기소개서 문항]
"{question}"

📌 작성자에게 다음과 같은 형식으로 직접 조언하세요:
- 어떤 JD 항목을 중심으로 쓰면 좋은지
- 어떤 경험(예: 프로젝트, 협업, 문제해결)을 중심으로 서술하면 좋은지
- 문단의 흐름이나 키워드 배열은 어떻게 하면 좋은지
- "부합한다", "잘 맞는다" 같은 추상적인 표현은 절대 사용하지 마세요
- 독자가 바로 이해할 수 있도록, 구체적인 문장 예시나 표현 방식을 추천하세요

말투는 "~하는 것이 좋습니다." 형태의 조언형 서술로, 총 5~7문장 이내로 구성하세요.
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
