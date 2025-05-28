import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

DATA_DIR = Path("./data")
CHART_DIR = Path("./charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "AppleGothic"
plt.style.use("default")

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

def chart_stock_generator():
    """0521.py 방식: LLM 에이전트를 사용해 stock 차트 생성"""
    stock_data = pd.read_csv(DATA_DIR / "stock_data.csv")
    custom_prefix = """
    Create a clean time-series Stock Chart from stock_data.
    Save the chart as 'stock_chart.png' in './charts' folder.
    Stock_data path is './data/stock_data.csv'.
    Use only English for title and axis labels.
    """

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(model_name="gpt-4o"),
        stock_data,
        verbose=True,
        allow_dangerous_code=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        prefix=custom_prefix,
    )
    result = agent.invoke("draw stock chart")
    return result


def chart_revenue_generator():
    """0521.py 방식: LLM 에이전트를 사용해 revenue 차트 생성"""
    revenue_data = pd.read_csv(DATA_DIR / "revenue_data.csv")
    priority_cols = ["매출액", "영업이익", "당기순이익", "자산총계"]
    valid_col = None
    for col in priority_cols:
        if col in revenue_data.columns and revenue_data[col].notna().all():
            valid_col = col
            break

    if valid_col:
        revenue_data = revenue_data[["종목코드", "연도", valid_col]]
        print(f"선택된 지표 컬럼: {valid_col}")
    else:
        raise ValueError("모든 지표 컬럼에 결측치가 존재합니다.")

    custom_prefix = """
    Please make the Shrink Line graph and save in './charts' folder.
    Save the chart as 'revenue_chart.png' in './charts' folder.
    revenue_data path is './data/revenue_data.csv'.
    Use only English for title and axis labels.
    """

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(model_name="gpt-4o"),
        revenue_data,
        verbose=True,
        allow_dangerous_code=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        prefix=custom_prefix,
    )
    result = agent.invoke("draw revenue chart")
    return result


from PIL import Image

def concat_images(path1: Path, path2: Path, output_path: Path):
    img1 = Image.open(path1)
    img2 = Image.open(path2)
    dst = Image.new("RGB", (img1.width + img2.width, max(img1.height, img2.height)))
    dst.paste(img1, (0, 0))
    dst.paste(img2, (img1.width, 0))
    dst.save(output_path)
    print("✅ 차트 병합 완료:", output_path)

def to_windows_uri(path: Path) -> str:
    return path.resolve().as_uri()


def run(state: dict) -> dict:
    chart_stock_generator()
    chart_revenue_generator()

    stock_path = CHART_DIR / "stock_chart.png"
    revenue_path = CHART_DIR / "revenue_chart.png"
    combined_path = CHART_DIR / "finance_combined_chart.png"

    concat_images(stock_path, revenue_path, combined_path)

    state["finance_result"] = {
        "agent": "AgentFinance",
        "output": {
            "stock_chart_path": str(stock_path),
            "revenue_chart_path": str(revenue_path),
            "combined_chart_path": to_windows_uri(combined_path),
            "insight": "차트 기반 재무 인사이트는 추후 생성됩니다."
        },
        "error": None,
        "retry": False
    }
    return state

