# agents/interview_agent/summarize_tool.py

from llm_client.llm import llm
from agents.interview_agent.prompt_template import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT

def summarize(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    reviews = state.get("interview_reviews", "")

    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": SUMMARY_USER_PROMPT.format(company=company, job=job, reviews=reviews)
        }
    ]

    try:
        response = llm.chat.completions.create(model="solar-pro", messages=messages)
        summary_text = response.choices[0].message.content.strip()
        lines = [line.strip("1234. ").strip() for line in summary_text.split('\n') if line.strip()]
        state["interview_result"] = {
            "agent": "AgentInterview",
            "output": {"summary": {
                "면접 방식": lines[0] if len(lines) > 0 else "",
                "질문 난이도": lines[1] if len(lines) > 1 else "",
                "면접관 태도": lines[2] if len(lines) > 2 else "",
                "지원자 팁": lines[3] if len(lines) > 3 else ""
            }},
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
