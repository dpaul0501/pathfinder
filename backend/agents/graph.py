"""
PathFinder LangGraph Agent
- LLM: Groq (testing) or OpenAI (demo) — controlled by LLM_PROVIDER env var
- Tools: OpenClaw MCP skills (program search, mentor match, reddit pain)
- Pattern: ReAct agent via langgraph.prebuilt.create_react_agent
"""

import json
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from backend.tools.program_search import search_wa_programs
from backend.tools.mentor_match import match_mentor
from backend.tools.reddit_pain import get_reddit_pain

load_dotenv()

SYSTEM_PROMPT = """You are PathFinder — a youth opportunity navigator for Washington state.

Your job is to help youth (ages 14–26) find free tech programs they qualify for RIGHT NOW,
build a clear week-by-week micro-path, match them to a mentor who walked the same road,
and show them the job waiting at the end.

Rules:
- Only surface programs that are free or tuition-free. Never suggest paid courses.
- Never give life advice or act as a counselor. Be practical and specific.
- Always call search_wa_programs first to get real program data.
- Always call match_mentor after you know the program path.
- Return a JSON object in this exact structure:

{
  "profile": {
    "age": <int or null>,
    "location": "<city/county>",
    "demographics": ["<label>"],
    "goals": "<one sentence>",
    "constraints": "<schedule/income/childcare or none>"
  },
  "programs": [<program objects from search_wa_programs>],
  "micro_steps": [
    {"week": "Week 1–2", "action": "<specific task>", "program": "<program name>", "why": "<one line>"},
    {"week": "Week 3–4", "action": "<specific task>", "program": "<program name>", "why": "<one line>"},
    {"week": "Month 2", "action": "<specific task>", "program": "<program name>", "why": "<one line>"},
    {"week": "Month 3", "action": "<specific task>", "program": "<program name>", "why": "<one line>"}
  ],
  "job_destination": {
    "title": "<entry-level job title>",
    "salary_range": "$XX K–$XX K",
    "companies": ["<company>"],
    "timeline": "<realistic months to first job>"
  },
  "mentor": <mentor object from match_mentor>,
  "summary": "<2 sentence encouraging summary for the youth>"
}

Always respond with ONLY valid JSON — no markdown, no extra text."""


def _build_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=os.getenv("LLM_MODEL_GROQ", "llama-3.3-70b-versatile"),
            temperature=0.2,
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("LLM_MODEL_OPENAI", "gpt-4o-mini"),
            temperature=0.2,
        )
    else:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=os.getenv("LLM_MODEL_ANTHROPIC", "claude-haiku-4-5-20251001"),
            temperature=0.2,
        )


@tool
def search_programs(
    age: int | None = None,
    county: str | None = None,
    demographics: list[str] | None = None,
    schedule: str | None = None,
) -> str:
    """Search Washington state free tech programs by youth profile. Returns matched programs with eligibility, deadlines, and seat counts."""
    results = search_wa_programs(age=age, county=county, demographics=demographics, schedule=schedule)
    return json.dumps(results)


@tool
def find_mentor(
    program_ids: list[str] | None = None,
    demographics: list[str] | None = None,
    languages: list[str] | None = None,
) -> str:
    """Find the single best mentor match for a youth based on their program path and background."""
    result = match_mentor(program_ids=program_ids, demographics=demographics, languages=languages)
    return json.dumps(result)


@tool
def fetch_reddit_pain(max_posts: int = 4) -> str:
    """Fetch real Reddit posts showing youth pain around tech access — for the government intelligence panel."""
    posts = get_reddit_pain(max_posts=max_posts)
    return json.dumps(posts)


_tools = [search_programs, find_mentor, fetch_reddit_pain]
_llm = None
_agent = None


def _get_agent():
    global _llm, _agent
    if _agent is None:
        _llm = _build_llm()
        _agent = create_react_agent(
            _llm,
            _tools,
            prompt=SystemMessage(content=SYSTEM_PROMPT),
        )
    return _agent


async def run_pathfinder(user_message: str) -> dict:
    """Run the PathFinder agent and return structured JSON response."""
    agent = _get_agent()
    result = await agent.ainvoke({"messages": [{"role": "user", "content": user_message}]})

    last_message = result["messages"][-1].content

    # Extract JSON — agent should return pure JSON per system prompt
    try:
        # Strip markdown fences if model added them
        text = last_message.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {"error": "parse_failed", "raw": last_message}
