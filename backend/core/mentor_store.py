"""
Mentor feedback store — file-backed (JSON) for hackathon.
Mentors log case notes, flag complexity, mark HITL escalations.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

STORE_PATH = Path(__file__).parent.parent / "data" / "mentor_feedback.json"


def _load() -> dict:
    if not STORE_PATH.exists():
        return {"cases": [], "stats": {"ai_handled": 0, "hitl": 0, "total": 0}}
    with open(STORE_PATH) as f:
        return json.load(f)


def _save(data: dict):
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_stats() -> dict:
    return _load()["stats"]


def get_cases(limit: int = 20) -> list[dict]:
    data = _load()
    return data["cases"][-limit:][::-1]  # most recent first


def add_case(
    youth_summary: str,
    complexity: str,           # "ai_handled" | "hitl"
    mentor_id: str | None,
    note: str | None,
    program_recommended: str | None,
) -> dict:
    data = _load()

    case = {
        "id": len(data["cases"]) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "youth_summary": youth_summary,
        "complexity": complexity,
        "mentor_id": mentor_id,
        "note": note,
        "program_recommended": program_recommended,
    }

    data["cases"].append(case)
    data["stats"]["total"] += 1
    if complexity == "hitl":
        data["stats"]["hitl"] += 1
    else:
        data["stats"]["ai_handled"] += 1

    _save(data)
    return case


def seed_demo_cases():
    """Seed realistic demo cases so the dashboard isn't empty on first load."""
    data = _load()
    if data["stats"]["total"] > 0:
        return

    demo_cases = [
        ("17yo Latina, South Seattle, no experience → Ada Build path generated", "ai_handled", None, None, "ada-build-self"),
        ("19yo, dropped out, wants IT — eligibility unclear for GEAR UP", "hitl", "m4", "Carlos reviewed — redirected to WIOA Youth + NPower", "wioa-youth"),
        ("24yo single mom, childcare conflict with Ada Core schedule", "hitl", "m1", "Sarah flagged wrap-around support options. Referred to Year Up evening track.", "year-up"),
        ("16yo, South Seattle, interested in cybersecurity", "ai_handled", None, None, "gencyber-uw-tacoma"),
        ("18yo, foster youth, needs housing + training together", "hitl", "m4", "Escalated — Cascades Job Corps residential program recommended", "cascades-job-corps"),
        ("22yo, GED only, wants cloud certs", "ai_handled", None, None, "aws-skills-center"),
        ("17yo, LGBTQ+, uncomfortable in group settings", "hitl", "m3", "Priya connected 1:1. Recommended self-paced Ada Build first.", "ada-build-self"),
        ("15yo asking about Running Start CS", "ai_handled", None, None, "running-start"),
        ("21yo, undocumented, which programs apply?", "hitl", "m2", "Marcus verified: Ada Build, Ada Core, Computing for All, NPower — all open regardless of status.", "ada-build-self"),
        ("20yo, Tacoma, wants cybersecurity career", "ai_handled", None, None, "gencyber-uw-tacoma"),
    ]

    for summary, complexity, mentor_id, note, program in demo_cases:
        case = {
            "id": len(data["cases"]) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "youth_summary": summary,
            "complexity": complexity,
            "mentor_id": mentor_id,
            "note": note,
            "program_recommended": program,
        }
        data["cases"].append(case)
        data["stats"]["total"] += 1
        if complexity == "hitl":
            data["stats"]["hitl"] += 1
        else:
            data["stats"]["ai_handled"] += 1

    _save(data)