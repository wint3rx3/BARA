import pandas as pd
import json
from llm_client.llm import llm

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    df = pd.read_csv("data/JD_DB.csv")
    row = df[(df["기업명"] == company) & (df["직무명"] == job)]

    work = row["담당업무"].values[0] if not row.empty else ""
    requirement = row["필요역량"].values[0] if not row.empty else ""

    prompt = f"""
다음은 채용공고의 '담당업무'와 '필요역량' 정보입니다.

이 내용을 바탕으로 의미 단위로 핵심 항목을 정리하고, 각 항목마다 **간단한 한 줄 설명**을 붙여주세요.

- 경력 관련 내용은 제외
- 항목 수는 responsibilities, requirements 각각 3~5개
- 형식은 다음과 같이 key-value 형태(JSON)로
- 설명은 짧고 실무자가 직관적으로 이해할 수 있어야 합니다

출력 예시:
{{
  "responsibilities": {{
    "공정 개선": "생산 효율을 높이기 위한 개선 활동 수행",
    "설비 유지보수": "설비 이상을 조기에 파악하고 대응"
  }},
  "requirements": {{
    "문제 해결 능력": "예기치 못한 문제에 유연하게 대응",
    "협업 능력": "다른 부서와 원활한 커뮤니케이션"
  }}
}}

[담당업무]
{work}

[필요역량]
{requirement}
"""

    try:
        response = llm.chat.completions.create(
            model="solar-pro",
            messages=[{"role": "user", "content": prompt}]
        )
        jd_structured = json.loads(response.choices[0].message.content)
    except Exception as e:
        print("JD 구조화 실패:", e)
        jd_structured = {
            "responsibilities": {
                "직무 설명 없음": "JD 정보가 누락되었거나 분석에 실패했습니다."
            },
            "requirements": {
                "필요 역량 없음": "JD 정보가 누락되었거나 분석에 실패했습니다."
            }
        }

    state["jd_raw"] = json.dumps({"담당업무": work, "필요역량": requirement}, ensure_ascii=False)
    state["jd_structured"] = jd_structured
    return state
