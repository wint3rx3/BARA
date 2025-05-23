from typing import TypedDict, Optional, Literal, List, Dict

# 🔹 1. CompanyInfo
class CompanyInfoOutput(TypedDict):
    history: str
    address: str
    welfare: str
    greeting: str
    talent: str
    website: str
    business: str
    employees: str
    entry_salary: str
    avg_salary: str

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
    articles: List[NewsSummary]

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
    revenue_chart_path: str
    stock_chart_path: str
    insight: str

class FinanceResult(TypedDict):
    agent: Literal["AgentFinance"]
    output: Optional[FinanceOutput]
    error: Optional[str]
    retry: bool

# 🔹 4. Resume
class ResumeOutput(TypedDict):
    profile_comparison: list  # 합격자 vs 사용자 스펙 리스트
    jd_raw: str               # JD 원문 (JSON string)
    resume_raw: list[str]          # 자소서 원문 (답변1, 답변2)
    jd_alignment: dict        # JD와 자소서 정합성 평가 결과
    philosophy_alignment: dict  # 기업 철학과 자소서 정합성 평가

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

# 🔹 전체 상태
class State(TypedDict):
    user_input: dict
    company_info_result: Optional[CompanyInfoResult]
    news_result: Optional[NewsResult]
    finance_result: Optional[FinanceResult]
    resume_result: Optional[ResumeResult]
    interview_result: Optional[InterviewResult]
    coord_result: Optional[dict]
    pdf_result: Optional[dict] 

def get_initial_state(user_input: dict) -> State:
    return {
        "user_input": user_input,
        "news_result": None,
        "finance_result": None,
        "resume_result": None,
        "interview_result": None,
        "coord_result": None,
        "pdf_result": None,
        "company_info_result": None
    }
