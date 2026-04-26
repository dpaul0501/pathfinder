"""
OpenClaw MCP Server — exposes PathFinder AgentSkills via Model Context Protocol.
Run standalone: python -m backend.tools.mcp_server
LangGraph agent connects via langchain-mcp-adapters.
"""

import json
from mcp.server.fastmcp import FastMCP
from backend.tools.program_search import search_wa_programs, get_program_by_id
from backend.tools.mentor_match import match_mentor
from backend.tools.reddit_pain import get_reddit_pain

mcp = FastMCP("pathfinder-openclaw")


@mcp.tool()
def skill_search_wa_programs(
    age: int | None = None,
    county: str | None = None,
    demographics: list[str] | None = None,
    schedule: str | None = None,
    citizenship_required: bool | None = None,
) -> str:
    """
    Search Washington state youth tech programs by eligibility profile.
    Returns up to 6 matched programs with deadlines, seats, and cost info.
    """
    results = search_wa_programs(
        age=age,
        county=county,
        demographics=demographics,
        schedule=schedule,
        citizenship_required=citizenship_required,
    )
    return json.dumps(results, indent=2)


@mcp.tool()
def skill_match_mentor(
    program_ids: list[str] | None = None,
    demographics: list[str] | None = None,
    languages: list[str] | None = None,
) -> str:
    """
    Match a youth to the single best mentor based on their program path and background.
    Returns mentor name, company, quote, and contact info.
    """
    result = match_mentor(
        program_ids=program_ids,
        demographics=demographics,
        languages=languages,
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def skill_get_reddit_pain(max_posts: int = 5) -> str:
    """
    Fetch real Reddit posts showing youth pain around tech access and program discovery.
    Used for government intelligence dashboard — shows unanswered questions at scale.
    """
    posts = get_reddit_pain(max_posts=max_posts)
    return json.dumps(posts, indent=2)


if __name__ == "__main__":
    mcp.run()
