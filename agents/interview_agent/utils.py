# agents/interview_agent/utils.py

import re

def parse_qna_text(text: str):
    q1 = re.search(r"예상 질문 1: (.+)", text)
    a1 = re.search(r"모범 답안 1: (.+?)(?=예상 질문 2:|<|$)", text, flags=re.DOTALL)
    q2 = re.search(r"예상 질문 2: (.+)", text)
    a2 = re.search(r"모범 답안 2: (.+?)(?=<|$)", text, flags=re.DOTALL)
    tips_match = re.search(r"<.+?>\n(.+?)(?=\n\n|$)", text, flags=re.DOTALL)
    tips = [line.strip(" 1234567890.-") for line in tips_match.group(1).split("\n") if line.strip()] if tips_match else []
    return {
        "question_1": q1.group(1).strip() if q1 else "",
        "answer_1": a1.group(1).strip() if a1 else "",
        "question_2": q2.group(1).strip() if q2 else "",
        "answer_2": a2.group(1).strip() if a2 else "",
        "tips": tips
    }
