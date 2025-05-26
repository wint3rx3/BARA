from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

TEMPLATE_DIR = os.path.dirname(__file__)

KOR_LABELS = {
    "greeting": "신년사",
    "talent": "인재상",
    "business": "사업내용",
    "employees": "직원수",
    "entry_salary": "신입사원 초봉",
    "avg_salary": "평균연봉"
}

def generate_pdf(state: dict, output_path: str = "output_report.pdf"):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("default_report.html")

    interview_result = state.get("interview_result", {}).get("output", {}) or {}
    resume_output = state.get("resume_result", {}).get("output", {}) or {}

    # ✅ 인성 질문 제거
    interview_qna = {
        k: v for k, v in interview_result.items()
        if k not in ["summary", "인성 질문", "직무 질문"]
    }

    # ✅ 실제 내용이 있는 역량만 추림
    raw_interview_hard = {
        "잠재역량": interview_result.get("potential", {}),
        "조직관계역량": interview_result.get("communication", {}),
        "직무역량": interview_result.get("competency", {}),
        "인성역량": interview_result.get("personality", {}),
    }
    interview_hard = {
        k: v for k, v in raw_interview_hard.items()
        if isinstance(v, dict) and any(val for val in v.values() if isinstance(val, str) and val.strip())
    }

    # ✅ 뉴스 출력 구조
    news_output = state.get("news_result", {}).get("output", {}) or {}
    기업뉴스 = news_output.get("기업뉴스", [])
    직무뉴스 = news_output.get("직무뉴스", [])

    html = template.render(
        기업명=state["user_input"].get("기업명", ""),
        직무명=state["user_input"].get("직무명", ""),

        finance=state.get("finance_result", {}).get("output", {}),

        기업뉴스=기업뉴스,
        직무뉴스=직무뉴스,

        resume=resume_output,
        profile_comparison=resume_output.get("profile_comparison", []),
        jd_structured=resume_output.get("jd_structured", {}),  # ✅ 채용공고 요약
        resume_questions=resume_output.get("resume_questions", []),  # ✅ 질문별 분석 리스트

        interview_summary=interview_result.get("summary", {}),
        interview_qna=interview_qna,
        interview_hard=interview_hard,

        company_info=state.get("company_info_result", {}).get("output", {}),
        company_info_labels=KOR_LABELS
    )

    HTML(string=html).write_pdf(output_path)
    print(f"📄 PDF 보고서 생성 완료 → {output_path}")
