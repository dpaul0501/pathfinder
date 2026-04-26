"""OpenClaw AgentSkill: match_mentor — finds best mentor match for a youth's path."""

import json
from pathlib import Path

_DATA = Path(__file__).parent.parent / "data" / "mentors.json"


def _load():
    with open(_DATA) as f:
        return json.load(f)


def match_mentor(
    program_ids: list[str] | None = None,
    demographics: list[str] | None = None,
    languages: list[str] | None = None,
) -> dict | None:
    """
    Match a mentor based on the youth's program path and demographics.
    Returns the single best match — not a marketplace.
    """
    mentors = _load()
    scored = []

    for m in mentors:
        if m["willingness"] == "none":
            continue
        score = 0

        # Path overlap — mentor walked the same programs
        if program_ids:
            overlap = set(program_ids) & set(m["path_taken"])
            score += len(overlap) * 3

        # Demographic resonance
        if demographics:
            for d in demographics:
                if any(d.lower() in md.lower() for md in m["demographic"]):
                    score += 2

        # Language match
        if languages:
            for lang in languages:
                if lang in m["languages"]:
                    score += 1

        # Availability weight
        avail_score = {"high": 2, "medium": 1, "low": 0}
        score += avail_score.get(m["willingness"], 0)

        scored.append((score, m))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]
