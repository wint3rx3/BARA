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

    topic_dict = {}
    for q, ans in zip([q1, q2], answers):
        try:
            parsed = ast.literal_eval(ans)
        except:
            parsed = {"value": [], "attitude": [], "experience": []}
        topic_dict[q] = parsed

    state["resume_raw"] = answers
    state["resume_topics"] = topic_dict
    return state
