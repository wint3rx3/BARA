# agents/finance_agent/get_code.py

import pandas as pd

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]

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

    code_list = [
        {"corp_name": "한국가스공사", "corp_code": "00261285", "ticker": "036460.KS"},
        {"corp_name": "LG화학", "corp_code": "00356361", "ticker": "051910.KS"},
        {"corp_name": "CJ제일제당", "corp_code": "00635134", "ticker": "097950.KS"},
        {"corp_name": "현대모비스", "corp_code": "00164788", "ticker": "012330.KS"},
        {"corp_name": "우리은행", "corp_code": "00254045", "ticker": "316140.KS"},
        {"corp_name": "LG에너지솔루션", "corp_code": "01515323", "ticker": "373220.KS"},
        {"corp_name": "중소기업은행", "corp_code": None, "ticker": "024110.KS"},
        {"corp_name": "현대건설", "corp_code": "00164478", "ticker": "000720.KS"},
        {"corp_name": "기아", "corp_code": "01664948", "ticker": "000270.KS"},
        {"corp_name": "GS", "corp_code": "00500254", "ticker": "078930.KS"},
        {"corp_name": "국민은행", "corp_code": "00104476", "ticker": "105560.KS"},
        {"corp_name": "LS", "corp_code": "00105952", "ticker": "006260.KS"},
        {"corp_name": "SK하이닉스", "corp_code": "00164779", "ticker": "000660.KS"},
        {"corp_name": "LG전자", "corp_code": "00401731", "ticker": "066570.KS"},
        {"corp_name": "한국전력공사", "corp_code": "00159193", "ticker": "015760.KS"},
        {"corp_name": "S-Oil", "corp_code": "00138279", "ticker": "010950.KS"},
        {"corp_name": "포스코인터내셔널","corp_code": "00124504","ticker": "047050.KS",},
        {"corp_name": "삼성전자", "corp_code": "00126380", "ticker": "005930.KS"},
        {"corp_name": "국민연금공단", "corp_code": "00706742", "ticker": None},
        {"corp_name": "현대글로비스", "corp_code": "00360595", "ticker": "086280.KS"},
        {"corp_name": "현대자동차", "corp_code": "00164742", "ticker": "005380.KS"},
        {"corp_name": "HD현대", "corp_code": "01205709", "ticker": "267250.KS"},
        {"corp_name": "한국산업은행", "corp_code": "00282455", "ticker": None},
        {"corp_name": "LG디스플레이", "corp_code": "00105873", "ticker": "034220.KS"},
        {"corp_name": "포스코홀딩스", "corp_code": None, "ticker": "005490.KS"},
        {"corp_name": "케이티", "corp_code": "00186461", "ticker": "030200.KS"},
        {"corp_name": "GS칼텍스", "corp_code": "00165459", "ticker": None},
        {"corp_name": "한화", "corp_code": "00160588", "ticker": "000880.KS"},
        {"corp_name": "SK이노베이션", "corp_code": "00631518", "ticker": "096770.KS"},
        {"corp_name": "국민건강보험공단", "corp_code": None, "ticker": None},
        {"corp_name": "SK", "corp_code": "00144155", "ticker": "034730.KS"},
        {"corp_name": "현대제철", "corp_code": "00145880", "ticker": "004020.KS"},
        {"corp_name": "쿠팡", "corp_code": "01019166", "ticker": "CPNG"},
    ]

    df = pd.DataFrame(code_list)

    # ✅ alias 정규화 매칭
    normalized_input = company.strip().replace(" ", "").lower()
    match_name = None
    for name, aliases in alias_map.items():
        all_names = [name] + aliases
        if any(normalized_input == alias.replace(" ", "").lower() for alias in all_names):
            match_name = name
            break

    if not match_name:
        state["finance_result"] = {
            "agent": "AgentFinance",
            "output": None,
            "error": f"'{company}'에 대한 코드/티커를 찾을 수 없습니다.",
            "retry": True
        }
        return state

    row = df[df["corp_name"] == match_name].iloc[0]

    state["corp_code"] = row["corp_code"]
    state["ticker"] = row["ticker"]
    state["finance_result"] = {
        "agent": "AgentFinance",
        "output": None,
        "error": None,
        "retry": False
    }

    print('get_code.py 실행완료')
    return state