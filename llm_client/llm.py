"""
# llm_client/llm.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1024,
    api_key=api_key
)
"""

# llm_client/llm.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1"
)


