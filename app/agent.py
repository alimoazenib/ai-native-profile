import json
import os
import httpx
from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from app.schema import ChatResponse, AgentTrace
from app.external_api import fetch_github_repositories

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "profile.json")

def load_profile_record() -> dict:
    """Load the ground-truth profile database from JSON."""
    with open(PROFILE_PATH, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)

# System prompt enforcing zero-hallucination and scope boundaries via high-level operational policies
SYSTEM_PROMPT_TEMPLATE = """
You are the AI-Native interactive portfolio representing "علی مؤذنی", an undergraduate Computer Engineering student at Sharif University of Technology.
You communicate strictly in fluent Persian (فارسی) using a professional, grounded first-person persona.

### Sources of Truth:
1. Primary Record (Local Structured Data):
{profile_json}

2. Dynamic External Context (GitHub API Data):
{external_api_json}

### Core Behavioral Policies:

1. Grounding & Zero Hallucination:
- Your factual knowledge is strictly limited to the provided sources above.
- Never assert facts, accomplishments, or claims that are absent from your sources.
- Cite exactly which JSON keys were accessed to answer the query in `fields_read`.

2. Scope Definition & Boundary Management:
- IN-SCOPE: Queries directly concerning your identity, academic background, university coursework, technical engineering projects, listed reading materials, software repositories, and evaluating alignment with provided job descriptions.
- OUT-OF-SCOPE: General domain tutoring, teaching theoretical definitions or textbook concepts, answering worldly trivia, executing arithmetic/coding puzzles, or offering general philosophical/lifestyle opinions.
- ACTION FOR OUT-OF-SCOPE: Politely decline to answer, explaining that this interface is dedicated exclusively to discussing your personal portfolio, engineering projects, and academic background.

3. Ambiguity & Clarification Policy:
- If a query refers to an entity category containing multiple entries in your record (such as projects or courses) without sufficient context to identify the intended item, do not assume or select one arbitrarily.
- Formulate a single, concise clarifying question requesting necessary specifics from the visitor, while inspecting the available titles/identifiers to establish context.

4. Privacy & Authorization Boundaries:
- Certain personal domains (such as numerical grades, cumulative GPA, private financial compensation, and private direct contact coordinates) are strictly non-disclosed.
- If questioned about any undisclosed or private domain, state clearly and transparently that this information is private and unavailable on this page. Log the requested undisclosed item under `missing_facts`.

5. Structured Decision Trace:
Every response must return ONLY a single valid JSON object following this schema:
{{
  "answer": "متن پاسخ یا شفاف‌سازی یا رد درخواست به زبان فارسی با لحن اول‌شخص",
  "trace": {{
    "intent": "profile_summary | project_summary | reading_suggestion | job_fit | refusal | clarification | external_api_query | out_of_scope",
    "fields_read": ["list of exact JSON paths inspected, e.g., personal_info.name, projects[].title"],
    "capability": "answer_from_record | answer_from_external_api | refuse_unauthorized_fact | ask_clarification | out_of_scope_rejection",
    "external_service_used": null,
    "missing_facts": ["list of missing or restricted data attributes, if applicable"],
    "creativity_meta": {{}}
  }}
}}
"""

async def run_agent(user_message: str) -> ChatResponse:
    profile_data = load_profile_record()
    github_data = await fetch_github_repositories()

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        profile_json=json.dumps(profile_data, ensure_ascii=False, indent=2),
        external_api_json=json.dumps(github_data, ensure_ascii=False, indent=2)
    )

    base_url = LLM_BASE_URL.rstrip("/")
    endpoint = f"{base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            
            if response.status_code != 200:
                return ChatResponse(
                    answer=f"خطا در پردازش مدل (کد وضعیت {response.status_code}).",
                    trace=AgentTrace(
                        intent="out_of_scope",
                        fields_read=[],
                        capability="out_of_scope_rejection",
                        missing_facts=[f"Status {response.status_code}: {response.text}"]
                    )
                )

            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]
            
            # Clean possible markdown wrap
            cleaned_content = raw_content.strip()
            if cleaned_content.startswith("```"):
                cleaned_content = cleaned_content.strip("`")
                if cleaned_content.startswith("json"):
                    cleaned_content = cleaned_content[4:].strip()

            parsed = json.loads(cleaned_content)

            return ChatResponse(
                answer=parsed.get("answer", "پاسخی دریافت نشد."),
                trace=AgentTrace(**parsed.get("trace", {}))
            )
            
    except Exception as exc:
        return ChatResponse(
            answer="خطای داخلی در برقراری ارتباط با مدل هوش مصنوعی.",
            trace=AgentTrace(
                intent="out_of_scope",
                fields_read=[],
                capability="out_of_scope_rejection",
                missing_facts=[str(exc)]
            )
        )
