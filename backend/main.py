"""PathFinder FastAPI backend."""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.graph import run_pathfinder
from backend.tools.reddit_pain import get_reddit_pain
from backend.routes.gov import router as gov_router

load_dotenv()

app = FastAPI(title="PathFinder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(gov_router)


class NavigateRequest(BaseModel):
    message: str


class RedditRequest(BaseModel):
    max_posts: int = 6


@app.get("/health")
def health():
    return {"status": "ok", "llm_provider": os.getenv("LLM_PROVIDER", "groq")}


@app.post("/api/navigate")
async def navigate(req: NavigateRequest):
    """Main endpoint: takes youth's message, returns personalized roadmap."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")
    result = await run_pathfinder(req.message)
    return result


@app.get("/api/reddit-pain")
async def reddit_pain(max_posts: int = 6):
    """Gov dashboard: returns real Reddit posts showing youth pain."""
    posts = get_reddit_pain(max_posts=max_posts)
    return {"posts": posts}


@app.get("/api/programs")
async def list_programs():
    """Return all WA programs (for the live programs panel)."""
    import json
    from pathlib import Path
    data_path = Path(__file__).parent / "data" / "wa_programs.json"
    with open(data_path) as f:
        return json.load(f)
