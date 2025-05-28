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
    formatted = []
    for item in news:
        if isinstance(item, dict):
            for title, summary in item.items():
                formatted.append(f"- {title}: {summary}")
    return "\n".join(formatted)


def run(state: dict) -> dict:
    stock_df = pd.read_csv("data/stock_data.csv")
    revenue_df = pd.read_csv("data/revenue_data.csv")

    # ✅ 뉴스 디버깅
    news_output = state.get("news_result", {}).get("output", {}) or {}
    기업뉴스 = news_output.get("기업뉴스", [])
    직무뉴스 = news_output.get("직무뉴스", [])
    news = 기업뉴스 + 직무뉴스
    stock_summary = summarize_dataframe(stock_df.tail(5), "주가")
    revenue_summary = summarize_dataframe(revenue_df, "매출")
    news_summary = format_news(news)

    # ✅ 프롬프트 확인 로그
    messages = [
        {
            "role": "system",
            "content": "당신은 취업 준비생을 위한 기업 보고서를 작성하는 전문 애널리스트입니다. 데이터와 뉴스 기반의 통찰력 있는 분석을 제공합니다."
        },
        {
            "role": "user",
            "content": f"""
    아래에 주어진 주가 요약, 매출 요약, 뉴스 요약 리스트를 참고하여 **1개의 문단**으로 된 인사이트를 작성하세요. 다음 조건을 반드시 반영하세요:

    📌 포함할 항목:
    1. 최근 주가의 상승/하락 추세와 특징 요약
    2. 최근 매출 데이터의 변화 및 수치 기반 평가
    3. 뉴스에서 드러난 이슈와 기업의 향후 리스크 또는 기회 분석
    4. 취업준비생 입장에서 중요하게 받아들여야 할 시사점

    🎯 작성 조건:
    - 반드시 **10줄 이내**의 문단으로 요약
    - **수치(%, 억 등)**는 필요한 경우 포함
    - **표현은 전문가적이면서도 이해하기 쉽게** 작성
    - **뉴스 요약 리스트**를 실제 참고한 것처럼 자연스럽게 통합
    - **한국어로 작성**하며, **공손하고 분석적인 문체** 사용

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
        parsed_result = json.loads(raw_result)
        insight_text = parsed_result["insight"]

    except Exception as e:
        print("🚨 LLM 호출 오류:", str(e))
        state["finance_result"] = {
            "agent": "AgentFinance",
            "output": None,
            "error": f"Upstage API 호출 또는 파싱 오류: {str(e)}",
            "retry": True
        }
        return state

    # 상태에 저장
    if "finance_result" not in state or not isinstance(state["finance_result"], dict):
        state["finance_result"] = {"agent": "AgentFinance", "output": {}, "error": None, "retry": False}
    if "output" not in state["finance_result"] or not isinstance(state["finance_result"]["output"], dict):
        state["finance_result"]["output"] = {}

    state["finance_result"]["output"]["insight"] = insight_text
    state["finance_result"]["agent"] = "AgentFinance"
    state["finance_result"]["error"] = None
    state["finance_result"]["retry"] = False

    print("✅ insight 최종 저장 완료")
    return state
