import re
from llm_client.llm import llm
from agents.interview_agent.prompt_template import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT

def remove_label_prefix(text: str, label: str) -> str:
    """
    '**면접 방식**:', '면접 방식:', '면접 방식' 등을 제거하고 내용만 반환.
    """
    pattern = rf"(\*\*{label}\*\*:?|{label}:?)"
    return re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

def summarize(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    reviews = state.get("interview_reviews", "")

    # ✅ 리뷰가 비어 있는 경우 graceful fallback
    if not reviews.strip():
        state["interview_result"] = {
            "agent": "AgentInterview",
            "output": {"summary": {
                "면접 방식": "",
                "질문 난이도": "",
                "면접관 태도": "",
                "지원자 팁": ""
            }},
            "error": None,
            "retry": False
        }
        return state

    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": SUMMARY_USER_PROMPT.format(company=company, job=job, reviews=reviews)}
    ]

    try:
        response = llm.chat.completions.create(model="solar-pro", messages=messages)
        summary_text = response.choices[0].message.content.strip()

        lines = [line.strip("1234. ").strip() for line in summary_text.split('\n') if line.strip()]

        summary_output = {
            "면접 방식": remove_label_prefix(lines[0], "면접 방식") if len(lines) > 0 else "",
            "질문 난이도": remove_label_prefix(lines[1], "질문 난이도") if len(lines) > 1 else "",
            "면접관 태도": remove_label_prefix(lines[2], "면접관 태도") if len(lines) > 2 else "",
            "지원자 팁": remove_label_prefix(lines[3], "지원자 팁") if len(lines) > 3 else ""
        }

        state["interview_result"] = {
            "agent": "AgentInterview",
            "output": {"summary": summary_output},
            "error": None,
            "retry": False
        }
    except Exception as e:
        state["interview_result"] = {
            "agent": "AgentInterview",
            "output": None,
            "error": f"요약 실패: {e}",
            "retry": True
        }

    return state