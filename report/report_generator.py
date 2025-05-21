from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def generate_pdf(state: dict, output_path: str = "output_report.pdf"):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("default_report.html")

    html = template.render(
        기업명=state["user_input"]["기업명"],
        직무명=state["user_input"]["직무명"],

        finance=state["finance_result"]["output"],
        news_list=state["news_result"]["output"]["뉴스"],
        resume=state["resume_result"]["output"],

        interview_summary=state["interview_result"]["output"]["summary"],
        interview_soft=state["interview_result"]["output"]["인성 질문"],
        interview_hard=state["interview_result"]["output"]["직무 질문"],

        company_info=state["company_info_result"]["output"]  # ✅ 추가
    )

    HTML(string=html).write_pdf(output_path)
    print(f"📄 PDF 보고서 생성 완료 → {output_path}")
