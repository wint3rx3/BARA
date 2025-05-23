# agents/resume_agent/compare_profiles_tool.py

import pandas as pd

def run(state: dict) -> dict:
    df = pd.read_csv("data/resume_data.csv")
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    matched = df[(df["기업명"] == company) & (df["직무명"] == job)]

    compare_list = []
    for _, row in matched.head(3).iterrows():
        compare_list.append({
            "source": "passer",
            "gpa": row.get("학점", ""),
            "language": row.get("어학", ""),
            "cert": row.get("자격증", ""),
            "award": row.get("수상", ""),
            "intern": row.get("인턴", ""),
            "club": row.get("동아리", "")
        })

    user = state["user_input"]["사용자_스펙"]
    user_cleaned = {
        "source": "user",
        "gpa": user.get("학점", ""),
        "language": user.get("어학", ""),
        "cert": user.get("자격증", []),
        "award": user.get("수상", []),
        "intern": user.get("인턴", ""),
        "club": user.get("동아리", "")
    }

    compare_list.append(user_cleaned)
    state["profile_comparison"] = compare_list
    return state
