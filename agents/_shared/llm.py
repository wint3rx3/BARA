# agents/_shared/llm.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # ✅ 핵심

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

default_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1024,
    api_key=api_key  # ✅ langchain_openai에선 'api_key' 파라미터
)
