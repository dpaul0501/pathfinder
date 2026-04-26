"""OpenClaw AgentSkill: search_wa_programs — filters WA programs by youth profile."""

import json
from pathlib import Path

_DATA = Path(__file__).parent.parent / "data" / "wa_programs.json"


def _load():
    with open(_DATA) as f:
        return json.load(f)


def search_wa_programs(
    age: int | None = None,
    county: str | None = None,
    demographics: list[str] | None = None,
    schedule: str | None = None,
    citizenship_required: bool | None = None,
    max_results: int = 6,
) -> list[dict]:
    """
    Filter WA state tech programs by youth profile.
    Returns programs sorted by fit: open seats first, then enrolling, then waitlist.
    """
    programs = _load()
    scored = []

    for p in programs:
        e = p["eligibility"]
        score = 0

        # Hard filters
        if age is not None:
            if e["age_min"] and age < e["age_min"]:
                continue
            if e["age_max"] and age > e["age_max"]:
                continue

        if citizenship_required is False and e.get("citizenship_required"):
            continue

        if county and e["counties"] != ["statewide"]:
            if county not in e["counties"]:
                continue

        if schedule and p["schedule"] not in ("self-paced", schedule, "varies"):
            pass  # soft preference, not hard filter

        # Scoring: demographic match
        if demographics:
            for d in demographics:
                if any(d.lower() in dp.lower() for dp in e["demographic_priority"]):
                    score += 2

        # Status scoring
        status_score = {"open": 3, "enrolling": 3, "applications_open": 3,
                        "active": 2, "waitlist": 1, "closed": 0}
        score += status_score.get(p["status"], 0)

        # Cost bonus
        if "free" in p["cost"]:
            score += 1

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:max_results]]


def get_program_by_id(program_id: str) -> dict | None:
    programs = _load()
    return next((p for p in programs if p["id"] == program_id), None)
