# graph/state_schema.py
from typing import TypedDict, Optional

class State(TypedDict):
    user_input: dict
    news_result: Optional[dict]
    finance_result: Optional[dict]
    resume_result: Optional[dict]
    interview_result: Optional[dict]
    coord_result: Optional[dict]
    pdf_result: Optional[dict]
    company_info_result: Optional[dict]

def get_initial_state(user_input: dict) -> State:
    return {
        "user_input": user_input,
        "news_result": None,
        "finance_result": None,
        "resume_result": None,
        "interview_result": None,
        "coord_result": None,
        "pdf_result": None
    }
