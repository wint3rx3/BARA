# agents/finance_agent/chart_generator.py

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path.cwd() / "data"
CHART_DIR = Path.cwd() / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

def to_windows_uri(path: Path) -> str:
    # Windows용 file URI: file:///C:/...
    return path.resolve().as_uri()

def generate_stock_chart_path() -> str:
    df = pd.read_csv(DATA_DIR / "stock_data.csv", index_col=0, parse_dates=True)

    plt.figure()
    plt.plot(df.index, df["Close"], marker="o")
    plt.title("Stock Price Over Time")
    plt.xlabel("Date")
    plt.ylabel("Close Price")

    chart_path = CHART_DIR / "stock_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return to_windows_uri(chart_path)

def generate_revenue_chart_path() -> str:
    df = pd.read_csv(DATA_DIR / "revenue_data.csv")

    if "매출액" in df.columns:
        df["매출액"] = df["매출액"].astype(str).str.replace(",", "")
        df = df[df["매출액"].str.isnumeric()]
        df["매출액"] = df["매출액"].astype(float)

    plt.figure()
    plt.plot(df["연도"], df["매출액"], marker="o")
    plt.title("Annual Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue (KRW)")

    chart_path = CHART_DIR / "revenue_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return to_windows_uri(chart_path)

def run(state: dict) -> dict:
    stock_path = generate_stock_chart_path()
    revenue_path = generate_revenue_chart_path()

    if "finance_result" not in state or not isinstance(state["finance_result"], dict):
        state["finance_result"] = {"agent": "AgentFinance", "output": {}, "error": None, "retry": False}
    elif "output" not in state["finance_result"] or state["finance_result"]["output"] is None:
        state["finance_result"]["output"] = {}

    state["finance_result"]["output"]["stock_chart_path"] = stock_path
    state["finance_result"]["output"]["revenue_chart_path"] = revenue_path

    return state
