# agents/finance_agent/fetch_data.py

import os
import pandas as pd
import yfinance as yf
import OpenDartReader
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path.cwd() / "data"
os.makedirs(DATA_DIR, exist_ok=True)

def run(state: dict) -> dict:
    ticker = state["ticker"]
    corp_code = state["corp_code"]

    # ✅ 1. 주가 데이터 수집
    start_date = "2023-01-01"
    end_date = "2025-04-30"
    stock = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if stock.empty:
        state["finance_result"] = {
            "agent": "AgentFinance",
            "output": None,
            "error": f"{ticker}에 대한 주가 데이터가 없습니다.",
            "retry": True
        }
        return state

    # 📌 Date 컬럼 명시 저장 (0521 방식)
    stock_df = stock[["Close"]].copy()
    stock_df.reset_index(inplace=True)  # Date 컬럼 확보
    stock_csv_path = DATA_DIR / "stock_data.csv"
    stock_df.to_csv(stock_csv_path, index=False)

    # ✅ 2. 재무제표 매출액 수집
    dart_api_key = os.getenv("DART_API_KEY")
    dart = OpenDartReader(dart_api_key)
    revenue_data = []
    account_map = {
        "매출액": ["매출액", "수익(매출액)", "영업수익", "매출"],
        "영업이익": ["영업이익", "영업이익(손실)"],
        "당기순이익": ["당기순이익", "당기순이익(손실)"],
        "자산총계": ["자산총계"]
    }

    for year in range(2018, 2025):
        try:
            fin = pd.DataFrame(dart.finstate(corp_code, year, reprt_code="11011"))
            row = {"연도": year, "종목코드": corp_code}
            for label, aliases in account_map.items():
                value = None
                for name in aliases:
                    match = fin.loc[fin["account_nm"] == name, "thstrm_amount"]
                    if not match.empty:
                        value = match.values[0]
                        break
                row[label] = value
            revenue_data.append(row)
        except Exception as e:
            print(f"{year}년 재무정보 수집 오류: {e}")

    revenue_df = pd.DataFrame(revenue_data)
    revenue_csv_path = DATA_DIR / "revenue_data.csv"
    revenue_df.to_csv(revenue_csv_path, index=False)

    # ✅ 상태 업데이트
    state["stock_df"] = str(stock_csv_path)
    state["revenue_df"] = str(revenue_csv_path)

    return state
