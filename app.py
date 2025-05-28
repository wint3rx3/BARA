import streamlit as st
import tempfile
import pandas as pd
from report.report_generator import generate_pdf
from graph.langgraph_runner import run_langgraph

# ✅ 기업명 alias_map 기반 정규화 목록
alias_map = {
        "삼성전자": ["samsung", "삼성전자주식회사", "주식회사삼성전자", "삼성전자(주)", "삼전",],
        "현대자동차": ["현대자동차 주식회사", "주식회사현대자동차", "현대자동차(주)", "현대차", "hyundaimotor", "현차",],
        "SK": ["에스케이", "sk(주)", "주식회사sk", "sk 주식회사", "sk그룹",],
        "국민건강보험공단": ["주식회사국민건강보험공단", "국민건강보험공단주식회사", "국민건강보험공단(주)", "건보공단",],
        "기아": ["기아(주)", "기아자동차", "주식회사기아", "기아주식회사", "기아차",],
        "한국전력공사": ["한국전력공사(주)", "한전", "한국전력공사주식회사", "주식회사한국전력공사", "kepco",],
        "LG전자": ["lg전자(주)", "lg전자주식회사", "주식회사lg전자", "엘지전자", "엘지",],
        "SK이노베이션": ["sk이노베이션(주)", "sk이노베이션주식회사", "주식회사sk이노베이션", "에스케이이노베이션",],
        "포스코홀딩스": ["포스코홀딩스주식회사", "포스코홀딩스(주)", "포스코", "주식회사포스코홀딩스", "포스코홀딩스",],
        "HD현대": ["hd현대(주)", "hd현대주식회사", "현대중공업지주", "주식회사hd현대", "현대지주",],
        "SK하이닉스": ["에스케이하이닉스", "주식회사sk하이닉스", "SK하이닉스(주)", "sk하이닉스주식회사", "하이닉스",],
        "현대모비스": ["현대모비스주식회사", "현대모비스(주)", "주식회사현대모비스",],
        "한화": ["주식회사한화", "한화(주)", "한화주식회사", "한화그룹",],
        "LG화학": ["lg화학(주)", "주식회사lg화학", "엘지화학", "lg화학주식회사",],
        "GS칼텍스": ["주식회사gs칼텍스", "gs칼텍스(주)", "gs칼텍스주식회사", "칼텍스",],
        "한국가스공사": ["한국가스공사(주)", "한국가스공사주식회사", "주식회사한국가스공사", "가스공사",],
        "한국산업은행": ["주식회사한국산업은행", "한국산업은행(주)", "산업은행", "한국산업은행 주식회사",],
        "국민은행": ["국민은행(주)", "KB국민은행", "주식회사국민은행", "국민은행주식회사", "kb",],
        "국민연금공단": ["국민연금공단(주)", "주식회사국민연금공단", "NPS", "국민연금공단 주식회사", "nps",],
        "S-Oil": ["s오일", "s-oil(주)", "주식회사s-oil", "s-oil 주식회사", "에쓰오일", "soil",],
        "우리은행": ["우리은행(주)", "주식회사우리은행", "우리은행주식회사", "우리", "woori",],
        "현대건설": ["현대건설 주식회사", "주식회사현대건설", "현대건설(주)", "현건",],
        "포스코인터내셔널": ["포스코인터내셔널(주)", "주식회사포스코인터내셔널", "포스코인터내셔널 주식회사",],
        "쿠팡": ["쿠팡주식회사", "주식회사쿠팡", "쿠팡(주)", "coupang",],
        "CJ제일제당": ["cj제일제당(주)", "cj", "cj제일제당주식회사", "주식회사cj제일제당", "씨제이제일제당",],
        "현대글로비스": ["현대글로비스주식회사", "현대글로비스(주)", "주식회사현대글로비스", "글로비스",],
        "LS": ["ls(주)", "ls주식회사", "주식회사ls", "엘에스",],
        "LG디스플레이": ["엘지디스플레이", "lg디스플레이(주)", "주식회사lg디스플레이", "lg디스플레이주식회사", "엘지디스플레이",],
        "케이티": ["케이티(주)", "kt", "주식회사케이티", "케이티주식회사",],
        "중소기업은행": ["주식회사중소기업은행", "중소기업은행(주)", "중소기업은행주식회사", "기업은행",],
        "LG에너지솔루션": ["엘지에너지솔루션", "lg에너지솔루션(주)", "lg에너지솔루션주식회사", "주식회사lg에너지솔루션", "엘지에너지",],
        "GS": ["주식회사gs", "gs(주)", "gs주식회사", "gs그룹",],
        "현대제철": ["주식회사현대제철", "현대제철주식회사", "현대제철(주)",],
    }

# alias 역추적용 flatten set
flat_alias_set = set()
for name, aliases in alias_map.items():
    flat_alias_set.add(name.lower().replace(" ", ""))
    flat_alias_set.update(alias.lower().replace(" ", "") for alias in aliases)

# ✅ 사용자 입력 UI
st.title("📄 야, 너두 취업할 수 있어")

기업명_input = st.text_input("✅ 지원 기업명을 입력하세요 (예: 삼성전자)")
직무명 = st.selectbox("✅ 지원 직무명", [
    '개발', '교육', '금융/재무', '기획/경영', '데이터', '디자인',
    '마케팅/시장조사', '미디어/홍보', '법률/법무', '생산/제조',
    '생산관리/품질관리', '서비스/고객지원', '엔지니어링', '연구개발',
    '영업/제휴', '유통/무역', '의약', '인사/총무', '전문직', '특수계층/공공'
])

# 기업명 유효성 검사
normalized_name = 기업명_input.strip().lower().replace(" ", "")
기업명_유효 = normalized_name in flat_alias_set

if 기업명_input and not 기업명_유효:
    st.warning("⚠️ 입력한 기업명은 현재 지원되지 않거나 등록된 기업명이 아닙니다. 다시 확인해 주세요.")

# ✅ 스펙 입력
st.subheader("🧾 사용자 스펙 입력")
학력 = st.text_input("학점 예시: 4.5")
어학 = st.text_input("어학 예시: 토익 900")
자격증 = st.text_input("자격증 개수")
인턴 = st.text_input("인턴 경험 횟수")
수상 = st.text_input("수상 횟수")

# ✅ PDF 생성 버튼
if st.button("📄 보고서 생성 및 다운로드"):
    if not 기업명_유효:
        st.error("❌ 유효하지 않은 기업명입니다. 위 경고를 확인해 주세요.")
    else:
        with st.spinner("PDF 생성 중입니다..."):
            user_input = {
                "기업명": 기업명_input,
                "직무명": 직무명,
                "사용자_스펙": {
                    "학력": 학력,
                    "어학": 어학,
                    "자격증": [j.strip() for j in 자격증.split(",") if j.strip()],
                    "인턴": 인턴,
                    "수상": [j.strip() for j in 수상.split(",") if j.strip()]
                }
            }

            # ✅ 인터뷰 데이터 로딩 및 필터링
            interview_data = pd.read_csv("data/interview_data.csv")
            filtered = interview_data[
                (interview_data["기업명"] == user_input["기업명"]) &
                (interview_data["직무명"] == user_input["직무명"])
            ]
            interview_reviews = "\n\n".join(filtered["combined_text"].dropna().tolist())

            # ✅ 인터뷰 데이터 함께 전달
            state = run_langgraph(user_input, interview_data, interview_reviews)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                generate_pdf(state, output_path=tmp.name)
                st.success("✅ PDF 생성 완료!")
                st.download_button(
                    label="📥 PDF 다운로드",
                    data=open(tmp.name, "rb").read(),
                    file_name="기업_분석_보고서.pdf",
                    mime="application/pdf"
                )
