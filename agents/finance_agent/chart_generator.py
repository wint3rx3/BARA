
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator, FuncFormatter
from pathlib import Path

DATA_DIR = Path.cwd() / "data"
CHART_DIR = Path.cwd() / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

def to_windows_uri(path: Path) -> str:
    return path.resolve().as_uri()

# ✅ 한국 원화 축약 표시 함수
def billions_formatter(x, pos):
    return f'{int(x / 1e8)}억' if x >= 1e8 else f'{int(x / 1e4)}만'

def generate_combined_chart_path() -> str:
    stock_df = pd.read_csv(DATA_DIR / "stock_data.csv", index_col=0, parse_dates=True)
    revenue_df = pd.read_csv(DATA_DIR / "revenue_data.csv")

    if "매출액" in revenue_df.columns:
        revenue_df["매출액"] = revenue_df["매출액"].astype(str).str.replace(",", "")
        revenue_df = revenue_df[revenue_df["매출액"].str.isnumeric()]
        revenue_df["매출액"] = revenue_df["매출액"].astype(float)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 📈 주가 그래프
    axes[0].plot(stock_df.index, stock_df["Close"], marker="o", linewidth=2, alpha=0.8)
    axes[0].set_title("📉 Stock Price Over Time")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Close Price")
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].xaxis.set_major_locator(mdates.AutoDateLocator())
    axes[0].yaxis.set_major_locator(MaxNLocator(nbins=6))  # ✅ y축 간격 제한

    # 📊 매출 그래프
    axes[1].plot(revenue_df["연도"], revenue_df["매출액"], marker="o", linewidth=2)
    axes[1].set_title("💰 Annual Revenue")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Revenue (KRW)")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].yaxis.set_major_formatter(FuncFormatter(billions_formatter))  # ✅ 억 단위 축약
    axes[1].yaxis.set_major_locator(MaxNLocator(nbins=6))  # ✅ y축 개수 제한

    plt.tight_layout(pad=3.0)
    chart_path = CHART_DIR / "finance_combined_chart.png"
    plt.savefig(chart_path, dpi=150)
    plt.close()

    return to_windows_uri(chart_path)


def run(state: dict) -> dict:
    combined_chart_path = generate_combined_chart_path()

    if "finance_result" not in state or not isinstance(state["finance_result"], dict):
        state["finance_result"] = {"agent": "AgentFinance", "output": {}, "error": None, "retry": False}
    elif "output" not in state["finance_result"] or state["finance_result"]["output"] is None:
        state["finance_result"]["output"] = {}

    state["finance_result"]["output"]["combined_chart_path"] = combined_chart_path

    return state
