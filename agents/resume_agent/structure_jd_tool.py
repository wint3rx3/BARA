# agents/resume_agent/structure_jd_tool.py

import pandas as pd
import json
from llm_client.llm import llm  # ✅ 프로젝트 통합 LLM 클라이언트 사용

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    df = pd.read_csv("data/JD_DB.csv")
    row = df[(df["기업명"] == company) & (df["직무명"] == job)]

    work = row["담당업무"].values[0] if not row.empty else ""
    requirement = row["필요역량"].values[0] if not row.empty else ""

    messages = [
        {"role": "system", "content": "다음 채용공고의 '담당업무'와 '필요역량'을 기반으로 responsibilities, requirements 구조로 나눠 JSON으로 작성해줘."},
        {"role": "user", "content": f"담당업무: {work}\n필요역량: {requirement}"}
    ]

    try:
        response = llm.chat.completions.create(model="solar-pro", messages=messages)
        jd_structured = json.loads(response.choices[0].message.content)
    except:
        jd_structured = {
        "responsibilities": ["표시할 직무 설명이 없습니다. (JD 정보가 누락되었을 수 있습니다)"],
        "requirements": ["표시할 필요 역량이 없습니다. (JD 정보가 누락되었을 수 있습니다)"]
    }


    state["jd_raw"] = json.dumps({"담당업무": work, "필요역량": requirement}, ensure_ascii=False)
    state["jd_structured"] = jd_structured

    print("📄 JD 구조화 대상 (work):", work)
    print("📄 JD 구조화 대상 (requirement):", requirement)
    print("📄 LLM 결과:", jd_structured)

    return state
