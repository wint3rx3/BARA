import os
from jinja2 import Template
from pathlib import Path
import base64
from models import Agent1Output, Agent2Output, Agent3Output


def render_report(agent1: Agent1Output, agent2: Agent2Output, agent3: Agent3Output) -> str:
    """에이전트 결과를 받아 마크다운 템플릿을 채워넣어 문자열로 반환"""
    # 템플릿 로딩
    with open("report_template.md", "r", encoding="utf-8") as f:
        template_str = f.read()
    template = Template(template_str)

    # 이미지 base64 → data URI 형태로 변환
    def base64_to_data_url(base64_str: str) -> str:
        return f"data:image/png;base64,{base64_str}"

    rendered = template.render(
        기업명=agent1.기업명,
        직무명=agent1.직무명,
        기업이슈=agent1.뉴스["기업이슈"],
        직무이슈=agent1.뉴스["직무이슈"],

        사업내용=agent2.기본정보.사업내용,
        직원수=agent2.기본정보.직원수,
        초봉=agent2.기본정보.신입사원_초봉,
        평균연봉=agent2.기본정보.개발직무_평균연봉,
        복지=agent2.복지제도.dict(),

        재무정보=[r.dict() for r in agent2.재무정보],
        주가정보=agent2.주가정보,
        재무요약=agent2.재무분석_요약,
        매출차트_url=base64_to_data_url(agent2.시각화["매출차트"].이미지_base64),
        주가차트_url=base64_to_data_url(agent2.시각화["주가차트"].이미지_base64),

        합격자비교=agent3.합격자_비교.데이터,
        레이더차트_url=base64_to_data_url(agent3.시각화.이미지_base64),
        JD=agent3.JD_정보.dict(),
        자소서=[q.dict() for q in agent3.자소서_질문],
        후기=agent3.면접_정보["특징_후기"],
        질문=[q.dict() for q in agent3.면접_정보["질문_리스트"]],

        링크=agent2.링크
    )

    return rendered


def save_markdown_and_pdf(markdown: str, output_dir: str = "output") -> str:
    """마크다운을 .md와 .pdf로 각각 저장"""
    import markdown2
    from weasyprint import HTML

    os.makedirs(output_dir, exist_ok=True)

    # 마크다운 파일 저장
    md_path = os.path.join(output_dir, "report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    # PDF 저장
    html_str = markdown2.markdown(markdown, extras=["fenced-code-blocks", "tables"])
    pdf_path = os.path.join(output_dir, "report.pdf")
    HTML(string=html_str).write_pdf(pdf_path)

    return pdf_path