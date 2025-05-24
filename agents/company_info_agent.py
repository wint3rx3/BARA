# agents/company_info_agent.py

import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(__file__)).parent  # ⬅️ 한 단계만
DATA_DIR = BASE_DIR / "data"

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    company_info_df = pd.read_csv(DATA_DIR / "company_info.csv")

    # 🔹 복지 통합
    welfare_columns = [col for col in company_info_df.columns if col.startswith("복지_")]
    def merge_welfare_info(row):
        return " / ".join([
            f"{col.replace('복지_', '')}: {row[col]}"
            for col in welfare_columns if pd.notna(row[col]) and str(row[col]).strip()
        ])
    company_info_df["복지_통합"] = company_info_df.apply(merge_welfare_info, axis=1)

    # 🔹 기업 필터링
    row = company_info_df[company_info_df["회사명"].str.contains(company, na=False)].reset_index(drop=True)
    if row.empty:
        state["company_info_result"] = {
            "agent": "AgentCompanyInfo",
            "output": None,
            "error": f"{company}에 해당하는 기업 정보를 찾을 수 없습니다.",
            "retry": True
        }
        return state

    # 🔹 평균연봉 컬럼 처리
    avg_salary_col = f"{job}_평균연봉"
    avg_salary = row.at[0, avg_salary_col] if avg_salary_col in row.columns else "정보 없음"

    # 🔹 최종 결과 구성
    state["company_info_result"] = {
        "agent": "AgentCompanyInfo",
        "output": {
            "history": row.at[0, "연혁"],
            "address": row.at[0, "주소"],
            "welfare": row.at[0, "복지_통합"],
            "greeting": row.at[0, "짧은 신년사"] if "짧은 신년사" in row.columns else "정보 없음",
            "talent": row.at[0, "인재상"],
            "website": row.at[0, "홈페이지"],
            "business": row.at[0, "사업내용"],
            "employees": row.at[0, "직원수"],
            "entry_salary": row.at[0, "신입사원 초봉"],
            "avg_salary": avg_salary
        },
        "error": None,
        "retry": False
    }

    return {
    "company_info_result": state["company_info_result"]
}