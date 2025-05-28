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
    
    business_raw = row.at[0, "사업내용"]

    def split_business_lines(text, chunk_size=3):
        if not isinstance(text, str) or pd.isna(text):
            return "정보 없음"
        items = [item.strip() for item in text.split(",")]
        lines = [", ".join(items[i:i+chunk_size]) for i in range(0, len(items), chunk_size)]
        return "\n".join(lines)


    formatted_business = split_business_lines(business_raw)

    def format_talent(talent_str):
        segments = [seg.strip() for seg in talent_str.split("**") if seg.strip()]
        lines = []
        for i in range(0, len(segments)-1, 2):  # 카테고리-내용 쌍으로 처리
            category = segments[i].replace(":", "").strip()
            description = segments[i+1].lstrip(":").strip()
            lines.append(f"{i//2 + 1}️⃣ {category}: {description}")
        return "\n".join(lines)

    formatted_talent = format_talent(row.at[0, "인재상"])

    # 🔹 평균연봉 컬럼 처리
    avg_salary_col = f"{job}_평균연봉"
    avg_salary = row.at[0, avg_salary_col] if avg_salary_col in row.columns else "정보 없음"
    raw_employees = str(row.at[0, "직원수"]).replace(",", "").replace("명", "").strip()
    formatted_employees = f"{int(raw_employees):,}명"

    # 🔹 최종 결과 구성
    state["company_info_result"] = {
        "agent": "AgentCompanyInfo",
        "output": {
            "business": formatted_business,
            "employees": formatted_employees,
            "entry_salary": row.at[0, "신입사원 초봉"],
            "avg_salary": avg_salary,
            "talent": formatted_talent,
            "greeting": row.at[0, "짧은 신년사"] if "짧은 신년사" in row.columns else "정보 없음"
        },
        "error": None,
        "retry": False
    }

    return {
    "company_info_result": state["company_info_result"]
}

if __name__ == "__main__":
    # 샘플 입력값 구성
    test_state = {
        "user_input": {
            "기업명": "삼성전자",       # company_info.csv 내 포함된 기업
            "직무명": "생산/제조"       # 평균연봉 컬럼 존재하는 직무명
        }
    }

    result = run(test_state)
    print("📦 반환 결과:")
    from pprint import pprint
    print(result["company_info_result"]["output"])
