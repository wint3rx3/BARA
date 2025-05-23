from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

TEMPLATE_DIR = os.path.dirname(__file__)

KOR_LABELS = {
    "history": "연혁",
    "address": "주소",
    "welfare": "복지",
    "greeting": "신년사",
    "talent": "인재상",
    "website": "채용사이트",
    "business": "사업내용",
    "employees": "직원수",
    "entry_salary": "신입사원 초봉",
    "avg_salary": "평균연봉"
}

def generate_pdf(state: dict, output_path: str = "output_report.pdf"):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("default_report.html")

    interview_result = state.get("interview_result", {}).get("output", {})
    resume_output = state.get("resume_result", {}).get("output", {})  # ✅ 여기 추가

    html = template.render(
        기업명=state["user_input"].get("기업명", ""),
        직무명=state["user_input"].get("직무명", ""),
        finance=state.get("finance_result", {}).get("output", {}),
        news_list=state.get("news_result", {}).get("output", {}).get("articles", []),
        resume=resume_output,  # ✅ 수정됨 (쉼표 제거, 변수 분리)
        profile_comparison=resume_output.get("profile_comparison", {}),  # ✅ 추가
        jd_alignment=resume_output.get("jd_alignment", {}),              # ✅ 추가
        philosophy_alignment=resume_output.get("philosophy_alignment", {}),  # ✅ 추가
        interview_summary=interview_result.get("summary", {}),
        interview_qna={
            "잠재역량": interview_result.get("potential", {}),
            "조직관계역량": interview_result.get("communication", {}),
            "직무역량": interview_result.get("competency", {}),
            "인성역량": interview_result.get("personality", {}),
        },
        company_info=state.get("company_info_result", {}).get("output", {}),
        company_info_labels=KOR_LABELS
    )

    HTML(string=html).write_pdf(output_path)
    print(f"📄 PDF 보고서 생성 완료 → {output_path}")
