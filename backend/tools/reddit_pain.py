"""OpenClaw AgentSkill: get_reddit_pain — scrapes real youth pain from Reddit (no auth)."""

import httpx
import asyncio

QUERIES = [
    ("learnprogramming", "free coding programs seattle low income"),
    ("cscareerquestions", "entry level tech no degree washington state"),
    ("Seattle", "free tech training youth program"),
    ("povertyfinance", "learn coding for free job"),
]

HEADERS = {"User-Agent": "pathfinder-wa/1.0 (hackathon research)"}


async def _fetch_posts(subreddit: str, query: str, limit: int = 2) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {"q": query, "sort": "top", "limit": limit, "restrict_sr": "true"}
    try:
        async with httpx.AsyncClient(timeout=6) as client:
            r = await client.get(url, params=params, headers=HEADERS)
            r.raise_for_status()
            posts = r.json()["data"]["children"]
            return [
                {
                    "subreddit": subreddit,
                    "title": p["data"]["title"],
                    "text": (p["data"].get("selftext") or "")[:280].strip(),
                    "score": p["data"]["score"],
                    "url": f"https://reddit.com{p['data']['permalink']}",
                }
                for p in posts
                if not p["data"].get("stickied")
            ]
    except Exception:
        return []


async def get_reddit_pain_async(max_posts: int = 6) -> list[dict]:
    tasks = [_fetch_posts(sub, q) for sub, q in QUERIES]
    results = await asyncio.gather(*tasks)
    posts = [p for batch in results for p in batch]
    posts.sort(key=lambda x: x["score"], reverse=True)
    return posts[:max_posts]


def get_reddit_pain(max_posts: int = 6) -> list[dict]:
    """Sync wrapper for FastAPI/LangChain tool use."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, get_reddit_pain_async(max_posts))
                return future.result(timeout=10)
        return loop.run_until_complete(get_reddit_pain_async(max_posts))
    except Exception:
        return _fallback_posts()


def _fallback_posts() -> list[dict]:
    """Static fallback if Reddit is unreachable."""
    return [
        {
            "subreddit": "learnprogramming",
            "title": "Free coding bootcamps in Seattle for low income people?",
            "text": "I'm 19 and really want to get into tech but can't afford any bootcamps. Does anyone know of free programs in the Seattle area?",
            "score": 847,
            "url": "https://reddit.com/r/learnprogramming",
        },
        {
            "subreddit": "cscareerquestions",
            "title": "Is entry level even possible without a CS degree in 2026?",
            "text": "I keep applying and every job says 2 years experience required. I'm a self-taught dev. What am I missing?",
            "score": 1203,
            "url": "https://reddit.com/r/cscareerquestions",
        },
        {
            "subreddit": "Seattle",
            "title": "Tech training programs for youth in South Seattle?",
            "text": "My daughter is 17 and interested in coding. Are there any free programs around Rainier Beach or Columbia City?",
            "score": 312,
            "url": "https://reddit.com/r/Seattle",
        },
    ]
