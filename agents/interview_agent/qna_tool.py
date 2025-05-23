# agents/interview_agent/qna_tool.py

import pandas as pd
from llm_client.llm import llm
from agents.interview_agent.prompt_template import QNA_SYSTEM_PROMPT, QNA_USER_PROMPT
from agents.interview_agent.utils import parse_qna_text

def generate_qna(state: dict) -> dict:
    df: pd.DataFrame = state.get("interview_data")
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]

    if df is None or df.empty:
        state["interview_result"]["output"].update({
            "potential": {},
            "communication": {},
            "competency": {},
            "personality": {}
        })
        return state

    group_df = df[(df["기업명"] == company) & (df["직무명"] == job)]

    category_map = {
        1: "potential",      # 잠재역량
        2: "communication",  # 조직관계역량
        3: "competency",     # 직무역량
        4: "personality"     # 인성역량
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

        examples = "\n\n".join(cat_df["combined_text"].dropna().sample(min(3, len(cat_df))))
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
            qna_output[key] = parse_qna_text(text)
        except Exception as e:
            qna_output[key] = {"error": f"QnA 생성 실패: {e}"}

    state["interview_result"]["output"].update(qna_output)
    return state
