import json

def flatten_sar(answer):
    if isinstance(answer, dict):
        return "\n".join(f"{k}: {v}" for k, v in answer.items() if v)
    return answer

def clean_json_text(text: str) -> str:
    return text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

def parse_qna_text(text: str) -> dict:
    try:
        cleaned = clean_json_text(text)
        parsed = json.loads(cleaned)
        return {
            "질문 1": parsed.get("질문 1", ""),
            "답변 1": flatten_sar(parsed.get("답변 1", "")),
            "질문 2": parsed.get("질문 2", ""),
            "답변 2": flatten_sar(parsed.get("답변 2", "")),
            "tips": parsed.get("tips", []),
        }
    except json.JSONDecodeError as e:
        print("❌ JSON 파싱 실패:", e)
        return {
            "질문 1": "",
            "답변 1": "",
            "질문 2": "",
            "답변 2": "",
            "tips": []
        }
