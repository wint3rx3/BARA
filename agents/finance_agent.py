# agents/finance_agent.py

# agents/finance_agent.py

import matplotlib.pyplot as plt
from matplotlib import rc
import io
import base64

# ✅ 한글 폰트 설정
rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

def create_sales_chart(company: str) -> str:
    years = [2020, 2021, 2022, 2023]
    sales = [220, 250, 270, 300]

    plt.figure()
    plt.plot(years, sales, marker='o')
    plt.title(f"{company} 연도별 매출 추이")
    plt.xlabel("연도")
    plt.ylabel("매출 (억 원)")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    base64_img = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{base64_img}"

def run(state: dict) -> dict:
    company = state["user_input"]["기업명"]

    # 시각화 이미지 생성
    sales_chart = create_sales_chart(company)

    state["finance_result"] = {
        "agent": "AgentFinance",
        "output": {
            "매출": [220, 250, 270, 300],
            "시각화": sales_chart
        },
        "error": None,
        "retry": False
    }
    return state

