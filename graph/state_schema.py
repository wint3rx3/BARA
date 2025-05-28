from typing import TypedDict, Optional, Literal, List, Annotated, Dict
from pandas import DataFrame

# 🔹 1. CompanyInfo
class CompanyInfoOutput(TypedDict):
    business: str
    employees: str
    entry_salary: str
    avg_salary: str
    talent: str
    greeting: str

class CompanyInfoResult(TypedDict):
    agent: Literal["AgentCompanyInfo"]
    output: Optional[CompanyInfoOutput]
    error: Optional[str]
    retry: bool

# 🔹 2. News
class NewsSummary(TypedDict):
    title: str
    summary: str

class NewsOutput(TypedDict):
    기업: str
    직무: str
    기업뉴스: List[NewsSummary]
    직무뉴스: List[NewsSummary]

class NewsResult(TypedDict):
    agent: Literal["AgentNews"]
    output: Optional[NewsOutput]
    error: Optional[str]
    retry: bool

# 🔹 3. Finance
class FinanceInsightInput(TypedDict):
    stock_df: str  # CSV 경로 또는 base64 encoded
    revenue_df: str
    news_articles: List[NewsSummary]  # 기존 NewsOutput과 연결
    
class FinanceOutput(TypedDict):
    combined_chart_path: str
    insight: str

class FinanceResult(TypedDict):
    agent: Literal["AgentFinance"]
    output: Optional[FinanceOutput]
    error: Optional[str]
    retry: bool

# 🔹 4. Resume

class ResumeQuestion(TypedDict):
    question: str
    value: List[str]
    attitude: List[str]
    experience: List[str]
    jd_feedback: str
    philosophy_feedback: str

class ResumeOutput(TypedDict):
    profile_comparison: list
    jd_raw: str
    resume_raw: List[str]
    jd_structured: Dict[str, Dict[str, str]]  # ✅ 수정됨
    resume_questions: List[ResumeQuestion]

class ResumeResult(TypedDict):
    agent: Literal["AgentResume"]
    output: Optional[ResumeOutput]
    error: Optional[str]
    retry: bool

# 🔹 5. Interview
class QnAEntry(TypedDict):
    question_1: str
    answer_1: str
    question_2: str
    answer_2: str
    tips: List[str]

class InterviewOutput(TypedDict):
    summary: Dict[str, str]  # e.g., {"method": "...", "difficulty": "..."}
    potential: Optional[QnAEntry]
    communication: Optional[QnAEntry]
    competency: Optional[QnAEntry]
    personality: Optional[QnAEntry]

class InterviewResult(TypedDict):
    agent: Literal["AgentInterview"]
    output: Optional[InterviewOutput]
    error: Optional[str]
    retry: bool

# 🔹 Coord 검증용 중간 결과
class CoordStage1Result(TypedDict):
    agent: Literal["CoordStage1"]
    output: dict
    retry: bool
    error: Optional[str]

class CoordStage2Result(TypedDict):
    agent: Literal["CoordStage2"]
    output: dict
    retry: bool
    error: Optional[str]

# 🔹 전체 상태
class State(TypedDict):
    user_input: Annotated[dict, "input"]
    company_info_result: Optional[CompanyInfoResult]
    news_result: Optional[NewsResult]
    finance_result: Optional[FinanceResult]
    resume_result: Optional[ResumeResult]
    interview_result: Optional[InterviewResult]
    coord_result: Optional[dict]
    pdf_result: Optional[dict]
    interview_data: Optional[DataFrame]
    interview_reviews: Optional[str]
    coord_stage_1_result: Optional[CoordStage1Result]
    coord_stage_2_result: Optional[CoordStage2Result]

def get_initial_state(user_input: dict) -> State:
    return {
        "user_input": user_input,
        "news_result": None,
        "finance_result": None,
        "resume_result": None,
        "interview_result": None,
        "coord_result": None,
        "pdf_result": None,
        "company_info_result": None,
        "coord_stage_1_result": None,
        "coord_stage_2_result": None
    }

