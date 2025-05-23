# app.py

import streamlit as st
import tempfile
from report.report_generator import generate_pdf
from graph.langgraph_runner import run_langgraph

# ✅ 기업/직무 선택지
기업명_리스트 = [
    '삼성전자(주)', '현대자동차(주)', 'SK(주)', '국민건강보험공단', '기아(주)', '한국전력공사(주)',
    '한국전력공사', 'LG전자(주)', 'SK이노베이션(주)', '포스코홀딩스(주)', '에이치디현대(주)',
    '에스케이하이닉스(주)', '현대모비스(주)', '(주)한화', '(주)LG화학', 'GS칼텍스(주)',
    '한국가스공사', '한국산업은행', '(주)국민은행', '국민연금공단', 'S-Oil(주)', '(주)우리은행',
    '현대건설(주)', '(주)포스코인터내셔널', '쿠팡 주식회사', 'CJ제일제당(주)', '현대글로비스(주)',
    '(주)LS', '엘지디스플레이(주)', '(주)케이티', '중소기업은행', '(주)엘지에너지솔루션', '(주)GS',
    '현대제철(주)'
]

직무명_리스트 = [
    '개발', '교육', '금융/재무', '기획/경영', '데이터', '디자인',
    '마케팅/시장조사', '미디어/홍보', '법률/법무', '생산/제조',
    '생산관리/품질관리', '서비스/고객지원', '엔지니어링', '연구개발',
    '영업/제휴', '유통/무역', '의약', '인사/총무', '전문직', '특수계층/공공'
]

# ✅ 사용자 입력 UI
st.title("📄 야, 너두 취업할 수 있어")

기업명 = st.text_input("✅ 지원 기업명")
직무명 = st.selectbox("✅ 지원 직무명", 직무명_리스트)

st.subheader("🧾 사용자 스펙 입력")

학력 = st.text_input("학력 예시: 서울대학교 컴퓨터공학과")
어학 = st.text_input("어학 예시: 토익 900")
자격증 = st.text_input("자격증 예시: 정보처리기사, SQLD")
인턴 = st.text_input("인턴 경험 예시: 삼성전자 인턴")
수상 = st.text_input("수상 경력 예시: 교내 알고리즘 대회 대상")

# ✅ PDF 생성 버튼
if st.button("📄 보고서 생성 및 다운로드"):
    with st.spinner("PDF 생성 중입니다..."):
        user_input = {
            "기업명": 기업명,
            "직무명": 직무명,
            "사용자_스펙": {
                "학력": 학력,
                "어학": 어학,
                "자격증": [j.strip() for j in 자격증.split(",") if j.strip()],
                "인턴": 인턴,
                "수상": [j.strip() for j in 수상.split(",") if j.strip()]
            }
        }

        # LangGraph 실행
        state = run_langgraph(user_input)

        # 임시 파일로 PDF 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            generate_pdf(state, output_path=tmp.name)
            st.success("✅ PDF 생성 완료!")
            st.download_button(
                label="📥 PDF 다운로드",
                data=open(tmp.name, "rb").read(),
                file_name="기업_분석_보고서.pdf",
                mime="application/pdf"
            )
