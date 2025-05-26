# agents/finance_agent/chart_generator.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MaxNLocator
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

DATA_DIR = Path.cwd() / "data"
CHART_DIR = Path.cwd() / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1"
)

def to_windows_uri(path: Path) -> str:
    return path.resolve().as_uri()

def fallback_chart(stock_df, revenue_df, chart_path: Path):
    print("🛠 fallback 차트 생성 시작")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    try:
        stock_df["Date"] = pd.to_datetime(stock_df["Date"], errors="coerce")
        stock_df = stock_df.dropna(subset=["Date"])
        axes[0].plot(stock_df["Date"], stock_df["Close"], marker="o", linewidth=2)
        axes[0].set_title("📈 Stock Price Over Time")
        axes[0].set_xlabel("Date")
        axes[0].set_ylabel("Close")
        axes[0].xaxis.set_major_locator(mdates.AutoDateLocator())
        axes[0].tick_params(axis="x", rotation=45)
        axes[0].yaxis.set_major_locator(MaxNLocator(nbins=6))
    except Exception as e:
        print("⚠️ 주가 차트 오류:", str(e))

    try:
        revenue_df["매출액"] = revenue_df["매출액"].astype(str).str.replace(",", "")
        revenue_df = revenue_df[revenue_df["매출액"].str.isnumeric()]
        revenue_df["매출액"] = revenue_df["매출액"].astype(float)
        axes[1].plot(revenue_df["연도"], revenue_df["매출액"], marker="o", linewidth=2)
        axes[1].set_title("💰 Annual Revenue")
        axes[1].set_xlabel("Year")
        axes[1].set_ylabel("Revenue (KRW)")
        axes[1].tick_params(axis="x", rotation=45)
        axes[1].yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x / 1e8)}억'))
        axes[1].yaxis.set_major_locator(MaxNLocator(nbins=6))
    except Exception as e:
        print("⚠️ 매출 차트 오류:", str(e))

    plt.tight_layout(pad=3.0)
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print("✅ fallback 차트 저장 완료")

def run(state: dict) -> dict:
    stock_df = pd.read_csv(DATA_DIR / "stock_data.csv")
    revenue_df = pd.read_csv(DATA_DIR / "revenue_data.csv")
    chart_path = CHART_DIR / "finance_combined_chart.png"

    messages = [
        {
            "role": "system",
            "content": "You are an expert Python data visualization assistant using matplotlib."
        },
        {
            "role": "user",
            "content": """
You are given two DataFrames already loaded:
- stock_df: includes daily stock prices. Use 'Date' (datetime) as x-axis and 'Close' as y-axis.
- revenue_df: includes annual revenue data. Use '연도' (int) as x-axis and '매출액' (float) as y-axis.

Write complete matplotlib code to:
1. Create a 1-row 2-column subplot
2. Left: stock_df['Date'] vs stock_df['Close']
3. Right: revenue_df['연도'] vs revenue_df['매출액']
4. Save to './charts/finance_combined_chart.png' with dpi=150
5. Use English labels/titles and proper layout
"""
        }
    ]

    try:
        response = client.chat.completions.create(
            model="solar-pro",
            messages=messages,
        )
        code = response.choices[0].message.content.strip()
        print("🧠 생성된 LLM 코드:\n", code)

        # ✅ 마크다운 블록 제거 (```python ... ```)
        if code.startswith("```"):
            code = re.sub(r"^```(?:python)?", "", code.strip(), flags=re.IGNORECASE | re.MULTILINE)
            code = code.replace("```", "").strip()

        if "savefig" not in code or "finance_combined_chart" not in code:
            print("⚠️ 경고: 저장 코드 누락 가능성 있음!")

        local_vars = {
            "stock_df": stock_df,
            "revenue_df": revenue_df,
            "plt": plt,
            "Path": Path,
            "CHART_DIR": CHART_DIR
        }
        exec(code, {}, local_vars)

    except Exception as e:
        print("🚨 LLM 코드 실행 오류:", str(e))

    # ✅ 파일 존재 여부 확인 + fallback
    if not chart_path.exists():
        print("❌ LLM 차트 생성 실패 → fallback 사용")
        fallback_chart(stock_df, revenue_df, chart_path)

    # ✅ 상태 저장
    if "finance_result" not in state or not isinstance(state["finance_result"], dict):
        state["finance_result"] = {"agent": "AgentFinance", "output": {}, "error": None, "retry": False}
    elif "output" not in state["finance_result"] or state["finance_result"]["output"] is None:
        state["finance_result"]["output"] = {}

    state["finance_result"]["output"]["combined_chart_path"] = to_windows_uri(chart_path)
    return state
