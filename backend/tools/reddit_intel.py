"""
Reddit Intelligence — scrapes youth tech queries, categorizes with LLM,
detects gaps where no WA program exists to answer the need.
"""

import json
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

SUBREDDITS = [
    ("learnprogramming", "free coding programs seattle washington youth"),
    ("cscareerquestions", "entry level tech no degree washington state"),
    ("Seattle", "free tech training youth coding program"),
    ("povertyfinance", "learn coding free job tech career"),
    ("AskTeenagers", "coding career tech job future"),
    ("washingtonstate", "youth tech program coding free"),
]

HEADERS = {"User-Agent": "pathfinder-wa/1.0 (hackathon research — non-commercial)"}


async def _fetch(subreddit: str, query: str, limit: int = 3) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {"q": query, "sort": "top", "limit": limit, "restrict_sr": "true", "t": "year"}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(url, params=params, headers=HEADERS)
            r.raise_for_status()
            posts = r.json()["data"]["children"]
            return [
                {
                    "id": p["data"]["id"],
                    "subreddit": subreddit,
                    "title": p["data"]["title"],
                    "text": (p["data"].get("selftext") or "")[:400].strip(),
                    "score": p["data"]["score"],
                    "num_comments": p["data"]["num_comments"],
                    "url": f"https://reddit.com{p['data']['permalink']}",
                    "created_utc": p["data"]["created_utc"],
                }
                for p in posts
                if not p["data"].get("stickied") and p["data"]["title"]
            ]
    except Exception:
        return []


async def fetch_raw_posts(max_per_query: int = 3) -> list[dict]:
    tasks = [_fetch(sub, q, max_per_query) for sub, q in SUBREDDITS]
    results = await asyncio.gather(*tasks)
    seen = set()
    posts = []
    for batch in results:
        for p in batch:
            if p["id"] not in seen:
                seen.add(p["id"])
                posts.append(p)
    posts.sort(key=lambda x: x["score"], reverse=True)
    return posts


def _build_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=os.getenv("LLM_MODEL_GROQ", "llama-3.3-70b-versatile"), temperature=0)
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=os.getenv("LLM_MODEL_OPENAI", "gpt-4o-mini"), temperature=0)


CATEGORIZE_PROMPT = """You are analyzing Reddit posts from youth seeking tech career help.

For each post, extract:
- need_type: one of [find_program, financial_aid, mentorship, job_search, skill_gap, eligibility_question, no_response_needed]
- location_wa: true if they mention WA state / Seattle / specific WA city, else false
- age_mentioned: integer age if mentioned, else null
- urgency: high | medium | low
- theme: 3-word max label (e.g. "free bootcamp access", "entry level jobs", "no degree path")
- has_clear_answer: true if the post already has a good answer, false if the need is unmet

Return ONLY a JSON array with one object per post. No markdown, no extra text.

Posts:
{posts}"""


async def categorize_posts(posts: list[dict]) -> list[dict]:
    if not posts:
        return []
    llm = _build_llm()
    summaries = [
        {"index": i, "title": p["title"], "text": p["text"][:200]}
        for i, p in enumerate(posts)
    ]
    prompt = CATEGORIZE_PROMPT.format(posts=json.dumps(summaries))
    try:
        resp = await llm.ainvoke(prompt)
        text = resp.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        categories = json.loads(text.strip())
        for cat in categories:
            idx = cat.get("index", 0)
            if idx < len(posts):
                posts[idx].update(cat)
        return posts
    except Exception:
        return posts


def detect_gaps(categorized_posts: list[dict], programs: list[dict]) -> list[dict]:
    """
    Posts where need_type is actionable but no program clearly matches.
    These are policy gaps — what youth need that the system doesn't provide.
    """
    program_tags = set()
    for p in programs:
        program_tags.update(p.get("tech_focus", []))
        program_tags.add(p.get("type", ""))

    gaps = []
    for post in categorized_posts:
        need = post.get("need_type", "")
        has_answer = post.get("has_clear_answer", True)
        if need in ("find_program", "financial_aid", "skill_gap", "eligibility_question") and not has_answer:
            gaps.append({
                "title": post["title"],
                "theme": post.get("theme", "unknown"),
                "need_type": need,
                "urgency": post.get("urgency", "medium"),
                "location_wa": post.get("location_wa", False),
                "url": post["url"],
                "score": post["score"],
            })

    gaps.sort(key=lambda x: (x["urgency"] == "high", x["score"]), reverse=True)
    return gaps[:10]


def aggregate_themes(categorized_posts: list[dict]) -> list[dict]:
    """Roll up top themes with counts for the gov dashboard chart."""
    from collections import Counter
    theme_counter: Counter = Counter()
    for p in categorized_posts:
        t = p.get("theme")
        if t:
            theme_counter[t] += 1
    return [{"theme": t, "count": c} for t, c in theme_counter.most_common(8)]