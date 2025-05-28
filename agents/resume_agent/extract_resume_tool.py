import pandas as pd
import ast
import json
from llm_client.llm import llm

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    df = pd.read_csv("data/resume_data.csv")
    row = df[(df["기업명"] == company) & (df["직무명"] == job)]

    if not row.empty:
        q1 = row["질문1"].values[0]
        q2 = row["질문2"].values[0]
        answers = [row["답변1"].values[0], row["답변2"].values[0]]
    else:
        q1, q2 = "질문 없음", "질문 없음"
        answers = ["{}", "{}"]

    resume_questions = []

    for q, ans in zip([q1, q2], answers):
        try:
            parsed = ast.literal_eval(ans)
        except Exception:
            parsed = {"value": [], "attitude": [], "experience": []}

        # 🔍 LLM 필터링: 해당 직무와 유의미한 키워드만 유지
        filter_prompt = f"""
다음은 자기소개서에서 추출된 주요 내용입니다. 
이 중 "{job}" 직무와 관련성이 높은 항목만 남겨주세요.

출력은 다음과 같은 JSON 형태로, 원래 항목명을 유지하며 관련 없는 내용은 제거해주세요.

예시:
{{
  "value": [...],
  "attitude": [...],
  "experience": [...]
}}

내용:
{json.dumps(parsed, ensure_ascii=False)}
"""

        try:
            response = llm.chat.completions.create(
                model="solar-pro",
                messages=[{"role": "user", "content": filter_prompt}]
            )
            filtered = json.loads(response.choices[0].message.content)
        except Exception as e:
            print("❌ 필터링 오류:", e)
            filtered = parsed

        resume_questions.append({
            "question": q,
            "value": filtered.get("기업성", []),
            "attitude": filtered.get("태도", []),
            "experience": filtered.get("핵심경험", []),
            "jd_feedback": "",  # 이후 단계에서 채움
            "philosophy_feedback": ""
        })

    state["resume_raw"] = answers
    state["resume_questions"] = resume_questions

    state["resume_result"] = {
        "agent": "AgentResume",
        "output": {
            "resume_questions": resume_questions,
            "profile_comparison": [],
            "jd_raw": "",
            "resume_raw": answers,
            "jd_structured": {}
        },
        "error": None,
        "retry": False
    }
    
    answers = [row["답변1"].values[0], row["답변2"].values[0]]
    print("🧾 원본 답변:", answers)
    print("🧾 파싱된 키워드:", parsed)
    print("🧾 필터링 결과:", filtered)

    print("🧾 자소서 출력 확인:", state["resume_result"]["output"]["resume_questions"])

    return state
