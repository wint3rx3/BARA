import ast
import pandas as pd

def flatten_language(language) -> str:
    if isinstance(language, str):
        try:
            language = ast.literal_eval(language)
        except Exception:
            return language.strip()
    if isinstance(language, dict):
        return ", ".join(f"{k}: {v}" for k, v in language.items())
    return str(language).strip() if pd.notna(language) else ""

def flatten_field(field) -> str:
    if isinstance(field, str):
        try:
            field = ast.literal_eval(field)
        except Exception:
            return field.strip()
    if isinstance(field, list):
        return ", ".join(str(x) for x in field if str(x).strip())
    if isinstance(field, dict):
        return ", ".join(f"{k}: {v}" for k, v in field.items())
    if isinstance(field, (float, int)):
        return str(int(field)) if float(field).is_integer() else str(field)
    return str(field).strip() if pd.notna(field) else ""


def run(state: dict) -> dict:
    df = pd.read_csv("data/resume_data.csv")
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    matched = df[(df["기업명"] == company) & (df["직무명"] == job)]

    compare_list = []
    for idx, (_, row) in enumerate(matched.head(3).iterrows(), start=1):
        compare_list.append({
            "source": f"합격자 {idx}",
            "gpa": flatten_field(row.get("학점", "")),
            "language": flatten_language(row.get("어학", "")),
            "cert": flatten_field(row.get("자격증", "")),
            "award": flatten_field(row.get("수상", "")),
            "intern": flatten_field(row.get("인턴", "")),
            "club": flatten_field(row.get("동아리", ""))
        })

    user = state["user_input"]["사용자_스펙"]
    user_cleaned = {
        "source": "나",
        "gpa": flatten_field(user.get("학점", "")),
        "language": flatten_language(user.get("어학", "")),
        "cert": flatten_field(user.get("자격증", "")),
        "award": flatten_field(user.get("수상", "")),
        "intern": flatten_field(user.get("인턴", "")),
        "club": flatten_field(user.get("동아리", ""))
    }

    compare_list.append(user_cleaned)
    state["profile_comparison"] = compare_list
    return state