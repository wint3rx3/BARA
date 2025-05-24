# agents/finance_agent/analyze_insight.py

import os
import pandas as pd
import json
from typing import List
from openai import OpenAI  # pip install openai
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1"
)

def summarize_dataframe(df: pd.DataFrame, label: str) -> str:
    if df.empty:
        return f"{label} 데이터가 없습니다."
    return df.to_string(index=False)

def format_news(news: List[dict]) -> str:
    if not news:
        return "관련 뉴스가 없습니다."
    return "\n".join([f"- {item['title']}: {item['summary']}" for item in news])

def run(state: dict) -> dict:
    stock_df = pd.read_csv("data/stock_data.csv")
    revenue_df = pd.read_csv("data/revenue_data.csv")
    news = state.get("news_result", {}).get("output", {}).get("articles", [])

    stock_summary = summarize_dataframe(stock_df.tail(5), "주가")
    revenue_summary = summarize_dataframe(revenue_df, "매출")
    news_summary = format_news(news)

    messages = [
        {
            "role": "system",
            "content": "당신은 취업 준비생을 위한 기업 보고서를 작성하는 전문 분석가입니다."
        },
        {
            "role": "user",
            "content": f"""
주어진 기업에 대해 주가, 매출 데이터와 최신 뉴스 요약을 바탕으로 다음 내용을 포함한 인사이트를 작성하세요:

1. 최근 주가/매출의 변화 경향 및 특징
2. 뉴스 내용과의 연결성 있는 해석
3. 이 기업의 미래 가능성 또는 리스크
4. 취준생 입장에서 느낄 수 있는 핵심 요점

제약 조건:
- 10줄 이내로 요약
- 표 또는 수치는 선택적으로 포함
- 한국어로 작성

[주가 데이터 요약]
{stock_summary}

[매출 데이터 요약]
{revenue_summary}

[뉴스 요약 리스트]
{news_summary}
"""
        }
    ]

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "finance_insight",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "insight": {
                        "type": "string",
                        "description": "기업의 재무/뉴스 기반 인사이트 요약"
                    }
                },
                "required": ["insight"],
                "additionalProperties": False
            }
        }
    }

    try:
        response = client.chat.completions.create(
            model="solar-pro",
            messages=messages,
            response_format=response_format
        )
        raw_result = response.choices[0].message.content
        parsed_result = json.loads(raw_result)  # 👈 반드시 JSON 파싱
        insight_text = parsed_result["insight"]
    except Exception as e:
        state["finance_result"] = {
            "agent": "AgentFinance",
            "output": None,
            "error": f"Upstage API 호출 또는 파싱 오류: {str(e)}",
            "retry": True
        }
        return state

    # analyze_insight.py 내부 run 함수 말미에 다음과 같이 수정
    if "finance_result" not in state or not isinstance(state["finance_result"], dict):
        state["finance_result"] = {
            "agent": "AgentFinance",
            "output": {},
            "error": None,
            "retry": False
        }

    if "output" not in state["finance_result"] or not isinstance(state["finance_result"]["output"], dict):
        state["finance_result"]["output"] = {}

    # ⬇️ 기존 경로를 덮어쓰지 않고 insight만 추가
    state["finance_result"]["output"]["insight"] = insight_text
    state["finance_result"]["agent"] = "AgentFinance"
    state["finance_result"]["error"] = None
    state["finance_result"]["retry"] = False

    return state
