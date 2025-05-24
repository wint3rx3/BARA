import pandas as pd
from llm_client.llm import llm
from agents.interview_agent.prompt_template import QNA_SYSTEM_PROMPT, QNA_USER_PROMPT
from agents.interview_agent.utils import parse_qna_text

def generate_qna(state: dict) -> dict:
    df: pd.DataFrame = state.get("interview_data")
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    if df is None or df.empty:
        print("⚠️ interview_data가 없음 → QnA 생성 생략")
        state.setdefault("interview_result", {"agent": "AgentInterview", "output": {}, "error": None, "retry": False})
        state["interview_result"]["output"].update({
            "potential": {},
            "communication": {},
            "competency": {},
            "personality": {}
        })
        return state

    # 1. 기업명/직무명 필터
    group_df = df[
        df["기업명"].str.contains(company, case=False, na=False) &
        df["직무명"].str.contains(job, case=False, na=False)
    ]
    if group_df.empty:
        print("⚠️ 필터링된 데이터 없음 → 전체에서 샘플링")
        group_df = df.sample(min(30, len(df)))  # fallback: 전체에서 샘플링

    # 2. category 매핑
    category_map = {
        1: "potential",
        2: "communication",
        3: "competency",
        4: "personality"
    }

    label_map = {
        "potential": "잠재역량",
        "communication": "조직관계역량",
        "competency": "직무역량",
        "personality": "인성역량"
    }

    qna_output = {}

    for cat_num, key in category_map.items():
        cat_df = group_df[group_df["category"] == cat_num]
        if cat_df.empty:
            qna_output[key] = {}
            continue

        try:
            examples = "\n\n".join(cat_df["combined_text"].dropna().sample(min(3, len(cat_df))))
        except Exception as e:
            qna_output[key] = {"error": f"샘플링 실패: {e}"}
            continue

        messages = [
            {"role": "system", "content": QNA_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": QNA_USER_PROMPT.format(
                    company=company,
                    job=job,
                    category_name=label_map[key],
                    examples=examples
                )
            }
        ]

        try:
            response = llm.chat.completions.create(model="solar-pro", messages=messages)
            text = response.choices[0].message.content.strip()
            parsed = parse_qna_text(text)
            qna_output[key] = parsed
        except Exception as e:
            qna_output[key] = {"error": f"QnA 생성 실패: {e}"}


    state.setdefault("interview_result", {"agent": "AgentInterview", "output": {}, "error": None, "retry": False})
    state["interview_result"]["output"].update(qna_output)
    return state
