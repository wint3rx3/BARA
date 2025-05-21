from typing import Dict
import re
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatOpenAI(temperature=0.7, model="gpt-4")

# ✅ 구조화 요약 프롬프트
summary_prompt = PromptTemplate(
    input_variables=["company", "job", "reviews"],
    template="""
당신은 {company}의 {job} 직무 면접 리뷰를 분석하는 전문가입니다.

아래 항목에 따라 JSON 형식으로 요약해 주세요:

{{
  "면접 방식": "...",
  "질문 난이도": "...",
  "면접관 태도": "...",
  "지원자 팁": "..."
}}

※ 각 항목은 한두 문장으로 구체적인 사례를 들어 작성하세요.  
※ "후기가 있었다", "다양했다" 등은 피하고, 객관적으로 서술하세요.

면접 후기:
{reviews}
"""
)

# ✅ 질문 생성용 프롬프트
qna_prompt = PromptTemplate(
    input_variables=["company", "job", "category_name", "examples"],
    template="""
당신은 {company}의 "{job}" 직무 면접을 준비하는 지원자에게 도움을 주는 면접 질문 생성 전문가입니다.

다음은 "{category_name}" 역량 유형에 해당하는 실제 면접 질문 후기입니다.

예시:
{examples}

1. 공통된 평가 의도를 파악하고,
2. 예상 질문 2개를 생성하고,
3. 각 질문에 대해 SAR 구조 기반 모범 답안을 작성하고,
4. 마지막으로 면접 팁 3가지를 정리해 주세요.

출력 형식:
예상 질문 1: ...
모범 답안 1: ...

예상 질문 2: ...
모범 답안 2: ...

<중요 Point>
1. ...
2. ...
3. ...
"""
)

# ✅ 체인 구성
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
qna_chain = LLMChain(llm=llm, prompt=qna_prompt)

# ✅ 질문/답변 파싱
def parse_qna_text(text: str) -> Dict:
    q1 = re.search(r"예상 질문 1: (.+)", text)
    a1 = re.search(r"모범 답안 1: (.+?)(?=예상 질문 2:|<|$)", text, flags=re.DOTALL)
    q2 = re.search(r"예상 질문 2: (.+)", text)
    a2 = re.search(r"모범 답안 2: (.+?)(?=<|$)", text, flags=re.DOTALL)
    tips_match = re.search(r"<.+?>\n(.+?)(?=\n\n|$)", text, flags=re.DOTALL)
    tips = [line.strip(" 1234567890.-") for line in tips_match.group(1).split("\n") if line.strip()] if tips_match else []
    return {
        "question_1": q1.group(1).strip() if q1 else "",
        "answer_1": a1.group(1).strip() if a1 else "",
        "question_2": q2.group(1).strip() if q2 else "",
        "answer_2": a2.group(1).strip() if a2 else "",
        "tips": tips
    }

"""
# ✅ LangGraph-compatible 실행 함수
def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]
    job = state["user_input"]["직무명"]
    df: pd.DataFrame = state["user_input"]["면접후기_df"]

    # 🔹 면접 후기 전체 요약 (JSON 형태 문자열로 응답 유도)
    raw_reviews = "\n".join(df["후기"].dropna().astype(str).tolist())
    summary_text = summary_chain.run(company=company, job=job, reviews=raw_reviews)
    try:
        summary = eval(summary_text.strip())  # 문자열 → 딕셔너리
    except Exception:
        summary = {"면접 방식": "", "질문 난이도": "", "면접관 태도": "", "지원자 팁": ""}

    # 🔹 역량별 질문 생성
    category_map = {1: "잠재역량", 2: "조직관계역량", 3: "직무역량", 4: "인성역량"}
    qna_outputs = {}
    for cat, name in category_map.items():
        cat_df = df[df["category"] == cat]
        if cat_df.empty:
            continue
        examples = "\n\n".join(cat_df["combined_text"].dropna().sample(min(3, len(cat_df))).tolist())
        output = qna_chain.run(company=company, job=job, category_name=name, examples=examples)
        qna_outputs[name] = parse_qna_text(output)

    # 🔹 최종 출력 구조 (report_generator 대응)
    state["interview_result"] = {
        "agent": "AgentInterview",
        "output": {
            "summary": summary,
            "직무 질문": qna_outputs.get("직무역량", {}),
            "인성 질문": qna_outputs.get("인성역량", {})
        },
        "error": None,
        "retry": False
    }

    return state
"""

def run(state: dict) -> dict:
    state["interview_result"] = {
        "agent": "AgentInterview",
        "output": {
            "summary": {
                "면접 방식": "대면 면접, 2:1 형태로 30분 진행",
                "질문 난이도": "기초 개념 위주로 쉬운 편",
                "면접관 태도": "편안한 분위기",
                "지원자 팁": "자기소개서를 기반으로 사례 중심 답변 준비 필요"
            },
            "직무 질문": {
                "question_1": "최근 참여한 프로젝트에 대해 설명해주세요.",
                "answer_1": "웹 크롤러를 제작했고 성능을 높이기 위해 캐싱 구조를 도입했습니다.",
                "question_2": "REST API를 설계할 때 고려하는 점은?",
                "answer_2": "URL 설계, 응답 표준화, 예외 처리입니다.",
                "tips": ["프로젝트 구조를 말로 풀어 설명하는 연습", "기술 키워드 명확히 숙지", "실무 예시 중심"]
            },
            "인성 질문": {
                "question_1": "협업 중 갈등을 어떻게 해결했나요?",
                "answer_1": "의견 충돌 시 중재안을 제시하고 역할을 분담했습니다.",
                "question_2": "본인의 단점을 하나 말해주세요.",
                "answer_2": "너무 완벽하게 하려는 경향이 있어 속도가 느려지는 점이 있습니다.",
                "tips": ["솔직한 답변 준비", "개선 노력 강조", "과거 사례 포함"]
            }
        },
        "error": None,
        "retry": False
    }
    return state