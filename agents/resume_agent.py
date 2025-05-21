# agents/resume_agent.py

def run(state: dict) -> dict:
    user_spec = state["user_input"]["사용자_스펙"]

    # 가상의 합격자 데이터
    accepted_specs = [
        {"학력": "서울대 전기전자", "어학": "토익 930", "자격증": ["정보처리기사"], "인턴": "삼성전자", "수상": ["ICT 공모전 우수상"]},
        {"학력": "KAIST 전산학", "어학": "오픽 IH", "자격증": ["SQLD"], "인턴": "네이버", "수상": ["교내 알고리즘 경진대회 1위"]},
        {"학력": "고려대 컴공", "어학": "토익 900", "자격증": ["정보처리기사", "ADsP"], "인턴": "삼성 SDS", "수상": []}
    ]

    # 요약 비교 (간단 예시)
    summary = {
        "학력": f"{user_spec['학력']} - 상위권 대학과 유사",
        "어학": f"{user_spec['어학']} - 평균 수준",
        "자격증": f"{user_spec['자격증']} - 유사한 자격 보유",
        "인턴": f"{user_spec['인턴']} - 유사 기업 경험",
        "수상": f"{user_spec['수상']} - 수상 경험 있음"
    }

    # 자소서 추천 키워드 추출
    keywords = ["협업", "문제 해결", "자기주도성", "실무 경험", "기술 역량"]

    state["resume_result"] = {
        "agent": "AgentResume",
        "output": {
            "비교_요약": summary,
            "추천_키워드": keywords
        },
        "error": None,
        "retry": False
    }
    return state
