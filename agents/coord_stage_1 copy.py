from llm_client.llm import llm
from openai.types.chat import ChatCompletionMessageParam

POLITICAL_KEYWORDS = [
    "대통령", "총선", "후보", "국회", "국민의힘", "더불어민주당", "김문수", "윤석열",
    "정치", "선거", "청와대", "정당", "정계", "출마", "보수", "진보", "의원", "의정"
]

def judge_news_relevance(title: str, summary: str, company: str, job: str) -> bool:
    lowered = (title + summary).lower()
    if any(p.lower() in lowered for p in POLITICAL_KEYWORDS):
        print("🚫 정치성 기사 필터링됨:", title)
        return False

    messages = [
        {"role": "system", "content": "다음 뉴스가 이 회사나 직무, 혹은 해당 산업군과 간접적으로라도 관련이 있으면 'yes'로 판단하세요. 특별히 무관하거나 정치적인 경우만 'no'로 답하세요."},
        {"role": "user", "content": f"""
<뉴스 제목>
{title}

<뉴스 요약>
{summary}

회사명: {company}
직무명: {job}

이 뉴스는 위 회사나 직무와 실제로 관련이 있습니까?
"""}
    ]
    try:
        response = llm.chat.completions.create(model="solar-pro", messages=messages)
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print("관련성 판단 실패:", e)
        return False

def judge_duplicate_by_llm(title1: str, summary1: str, title2: str, summary2: str) -> bool:
    messages = [
        {"role": "system", "content": "다음 두 뉴스가 본질적으로 같은 내용인지 판단하세요. 같으면 'Yes', 다르면 'No'로만 답변하세요."},
        {"role": "user", "content": f"""
<뉴스 1 제목>
{title1}
<뉴스 1 요약>
{summary1}

<뉴스 2 제목>
{title2}
<뉴스 2 요약>
{summary2}

이 두 뉴스는 본질적으로 같은 내용입니까?
"""}
    ]
    try:
        response = llm.chat.completions.create(model="solar-pro", messages=messages)
        return "yes" in response.choices[0].message.content.lower()
    except Exception as e:
        print("중복 판단 실패:", e)
        return False

def filter_and_dedup(articles, company, job, label="기사"):
    relevant, irrelevant, deduped, duplicates = [], [], [], []

    print(f"\n📥 [{label} 기사 후보 목록] 총 {len(articles)}건")
    for i, a in enumerate(articles, 1):
        title, summary = a["제목"], a["기사"]
        is_relevant = judge_news_relevance(title, summary, company, job)
        status = "✅ 유효" if is_relevant else "❌ 관련 없음"
        print(f"{i}. {title} → {status}")
        (relevant if is_relevant else irrelevant).append(a if is_relevant else title)

    if len(relevant) <= 1:
        return relevant, [t for t in irrelevant if isinstance(t, str)], []

    # 2개 이상 유효한 경우 → 중복 여부 판단
    a, b = relevant[0], relevant[1]
    is_dup = judge_duplicate_by_llm(a["제목"], a["기사"], b["제목"], b["기사"])

    if is_dup:
        print(f"⛔ 중복 판단됨: \"{a['제목']}\" / \"{b['제목']}\" → 하나만 사용")
        return [a], [t for t in irrelevant if isinstance(t, str)], [b["제목"]]
    else:
        print(f"✅ 두 기사 모두 유효하고 중복 아님 → 둘 다 사용")
        return [a, b], [t for t in irrelevant if isinstance(t, str)], []

def run(state: dict) -> dict:
    user_input = state.get("user_input", {})
    company = user_input.get("기업명", "").strip()
    job = user_input.get("직무명", "").strip()
    corp_articles = state.get("기업기사리스트", [])
    job_articles = state.get("직무기사리스트", [])

    valid_corp, irr_corp, dup_corp = filter_and_dedup(corp_articles, company, job, "기업")
    valid_job, irr_job, dup_job = filter_and_dedup(job_articles, company, job, "직무")

    state["news_cache"] = {"기업": valid_corp, "직무": valid_job}

    retry, error_agents = False, []
    if len(valid_corp) < 2 or len(valid_job) < 2:
        retry = True
        reasons = []
        if len(valid_corp) < 2:
            reasons.append(f"기업 기사 부족 ({len(valid_corp)}/2)")
        if len(valid_job) < 2:
            reasons.append(f"직무 기사 부족 ({len(valid_job)}/2)")
        state["news_result"]["error"] = "유효 뉴스 부족 - " + ", ".join(reasons)
        state["news_result"]["retry"] = True
        error_agents.append(("AgentNews", state["news_result"]["error"]))
        state.setdefault("news_feedback_history", []).append({
            "irrelevant_titles": irr_corp + irr_job,
            "duplicate_titles": dup_corp + dup_job,
            "reason": "관련성 부족 또는 중복 뉴스로 인해 유효 뉴스 부족"
        })

    print("✅ [coord] 유효 기업 기사 수:", len(valid_corp))
    for a in valid_corp:
        print("   -", a["제목"])
    print("✅ [coord] 유효 직무 기사 수:", len(valid_job))
    for a in valid_job:
        print("   -", a["제목"])

    for agent, key, required_fields in [
        ("AgentFinance", "finance_result", ["revenue_chart_path", "stock_chart_path"]),
        ("AgentCompanyInfo", "company_info_result", ["address", "history"])
    ]:
        result = state.get(key)
        if not result or result.get("error") or result.get("retry"):
            error_agents.append((agent, "실행 실패 또는 오류"))
        else:
            output = result.get("output", {})
            if not all(output.get(k) for k in required_fields):
                error_agents.append((agent, "필수 필드 누락"))

    state["coord_stage_1_result"] = {
        "agent": "CoordStage1",
        "output": {
            "status": "오류" if error_agents else "정상",
            "문제_에이전트": error_agents
        },
        "retry": retry,
        "error": "CoordStage1 실패" if retry else None
    }

    return state