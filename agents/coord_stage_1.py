from llm_client.llm import llm
from openai.types.chat import ChatCompletionMessageParam
from itertools import combinations

def judge_news_relevance(title: str, summary: str, company: str, job: str) -> bool:
    POLITICAL_KEYWORDS = [
        "대통령", "총선", "후보", "국회", "국민의힘", "더불어민주당", "김문수", "윤석열",
        "정치", "선거", "청와대", "정당", "정계", "출마", "보수", "진보", "의원", "의정"
    ]
    
    lowered = (title + summary).lower()
    if any(p.lower() in lowered for p in POLITICAL_KEYWORDS):
        print("🚫 정치성 기사 필터링됨:", title)
        return False

    messages = [
        {
            "role": "system",
            "content": "다음 뉴스가 취업 준비에 실제 도움이 되는지 판단하세요. 회사 또는 직무 중심이면 'Yes', 아니면 'No'로만 답변하세요."
        },
        {
            "role": "user",
            "content": f"""
<뉴스 제목>
{title}

<뉴스 요약>
{summary}

회사명: {company}
직무명: {job}

이 뉴스는 위 회사나 직무와 실제로 관련이 있습니까?
"""
        }
    ]
    try:
        response = llm.chat.completions.create(model="solar-pro", messages=messages)
        result = response.choices[0].message.content.strip().lower()
        return "yes" in result
    except Exception as e:
        print("관련성 판단 실패:", e)
        return False  # 보수적으로 거부


def filter_and_dedup(articles, company, job, label="기사"):
    relevant = []
    irrelevant = []
    all_checked = []  # 전체 기사 저장용

    print(f"\n📥 [{label} 기사 후보 목록] 총 {len(articles)}건")

    for i, a in enumerate(articles, 1):
        title = a["제목"]
        summary = a["기사"]

        is_relevant = judge_news_relevance(title, summary, company, job)
        relevance_status = "✅ 유효" if is_relevant else "❌ 관련 없음"
        print(f"{i}. {title} → {relevance_status}")

        all_checked.append((title, relevance_status))

        if is_relevant:
            relevant.append(a)
        else:
            irrelevant.append(title)

    deduped = []
    duplicates = []

    for a in relevant:
        is_duplicate = False
        for b in deduped:
            if judge_duplicate_by_llm(a["제목"], a["기사"], b["제목"], b["기사"]):
                # 제목이 완전히 동일할 때만 중복으로 간주
                if a["제목"].strip() == b["제목"].strip():
                    is_duplicate = True
                    print(f"⛔ 중복 판단됨 (제목 동일): {a['제목']}")
                    duplicates.append(a["제목"])
                    break
                else:
                    print(f"⚠️ 유사한 기사지만 제목 다름 → 유지: {a['제목']}")
        if not is_duplicate:
            deduped.append(a)


def run(state: dict) -> dict:
    error_agents = []
    user_input = state.get("user_input", {})
    company = user_input.get("기업명", "").strip()
    job = user_input.get("직무명", "").strip()

    # 📥 기사 분리
    corp_articles = state.get("기업기사리스트", [])
    job_articles = state.get("직무기사리스트", [])

    # 🧪 관련성 + 중복 검사
    valid_corp, irrelevant_corp, dup_corp = filter_and_dedup(corp_articles, company, job, label="기업")
    valid_job, irrelevant_job, dup_job = filter_and_dedup(job_articles, company, job, label="직무")

    # ✅ 캐시 저장
    state["news_cache"] = {
        "기업": valid_corp,
        "직무": valid_job
    }

    # ✅ 재시도 조건
    retry = False
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
            "irrelevant_titles": irrelevant_corp + irrelevant_job,
            "duplicate_titles": dup_corp + dup_job,
            "reason": "관련성 부족 또는 중복 뉴스로 인해 유효 뉴스 부족"
        })

    print("✅ [coord] 유효 기업 기사 수:", len(valid_corp))
    for a in valid_corp:
        print("   -", a["제목"])

    print("✅ [coord] 유효 직무 기사 수:", len(valid_job))
    for a in valid_job:
        print("   -", a["제목"])


    # ✅ Finance 평가
    finance_result = state.get("finance_result")
    if not finance_result or finance_result.get("error") or finance_result.get("retry"):
        error_agents.append(("AgentFinance", "실행 실패 또는 오류"))
    else:
        out = finance_result.get("output", {})
        if not out or not out.get("revenue_chart_path") or not out.get("stock_chart_path"):
            error_agents.append(("AgentFinance", "차트 경로 누락"))

    # ✅ CompanyInfo 평가
    company_info_result = state.get("company_info_result")
    if not company_info_result or company_info_result.get("error") or company_info_result.get("retry"):
        error_agents.append(("AgentCompanyInfo", "실행 실패 또는 오류"))
    else:
        out = company_info_result.get("output", {})
        if not out or not out.get("address") or not out.get("history"):
            error_agents.append(("AgentCompanyInfo", "주소 또는 연혁 정보 누락"))

    # ✅ 결과 조립
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
