# agents/company_info_agent.py

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]

    output = {
        "연혁": f"{company}는 1970년에 설립되어 글로벌 기업으로 성장하였습니다.",
        "주소": "서울특별시 강남구 테헤란로 123",
        "복지": "사내 식당, 복지 포인트, 유연 근무제 등 제공",
        "채용사이트": f"https://recruit.{company.lower().replace('(주)', '').replace(' ', '').replace('.', '')}.com",
        "인재상": "창의성, 도전정신, 팀워크를 갖춘 인재",
        "신년사": "2024년은 디지털 혁신의 해입니다. 함께 도약합시다!"
    }

    state["company_info_result"] = {
        "agent": "AgentCompanyInfo",
        "output": output,
        "error": None,
        "retry": False
    }

    return state
