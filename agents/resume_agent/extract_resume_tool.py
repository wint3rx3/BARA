# agents/resume_agent/extract_resume_tool.py

import pandas as pd
import ast

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

        resume_questions.append({
            "question": q,
            "value": parsed.get("value", []),
            "attitude": parsed.get("attitude", []),
            "experience": parsed.get("experience", []),
            "jd_feedback": "",  # 빈값으로 초기화
            "philosophy_feedback": ""
        })

    state["resume_raw"] = answers
    state["resume_questions"] = resume_questions  # ✅ 핵심 변경점
    return state
