# agents/news_agent/extract_subthemes_tool.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1"
)

def run(state: dict) -> dict:
    titles = state.get("뉴스제목", [])
    recent_news = "\n".join(titles)

    messages = [
        {
            "role": "system",
            "content": "너는 뉴스 분석 전문가야. 제목들을 보고 주제와 서브주제를 JSON으로 뽑아줘."
        },
        {
            "role": "user",
            "content": f"""
다음 뉴스 제목들을 참고하여 JSON 형식으로 아래 구조를 엄격히 따르세요.

뉴스 제목 목록:
{recent_news}

형식 예시:
{{
  "theme": "반도체 산업 경쟁 심화",
  "sub_themes": ["삼성의 HBM 투자", "TSMC와의 기술 경쟁"]
}}
"""
        }
    ]

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "NewsletterTheme",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "sub_themes": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["theme", "sub_themes"],
                "additionalProperties": False
            }
        }
    }

    try:
        response = llm.chat.completions.create(
            model="solar-pro",
            messages=messages,
            response_format=response_format
        )
        content = response.choices[0].message.content
        sub_themes = eval(content)["sub_themes"]  # or json.loads
    except Exception as e:
        state["news_result"] = {
            "agent": "AgentNews",
            "output": None,
            "error": f"subtheme 추출 실패: {str(e)}",
            "retry": True
        }
        return state

    state["서브테마"] = sub_themes
    return state
