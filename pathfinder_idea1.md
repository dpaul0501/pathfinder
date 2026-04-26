# 🧭 PathFinder — Washington Youth Tech Navigator
### HSI x WiT Regatta Hackathon 2026 | Track: Youth Empowerment

---

## The Problem

Washington state has dozens of free programs for under-resourced youth entering tech. They're scattered across 12 agencies, 5 nonprofits, and 3 websites. No single navigation layer exists.

The data is damning:
- **~80K WA youth ages 16–24** are not in education, employment, or training (NEET)
- Only **32% of Latino youth** attain a post-secondary credential vs. 62% statewide
- **85% of Ada Developers Academy students** are low-income — the pipeline exists, but youth can't find it
- Washington's **FutureReady 2026** initiative is rewriting graduation requirements right now — explicitly noting that policy has historically been built *without input from underserved communities*

> *"State education policy has been developed in silos, often without sufficient input from the very communities it impacts most — students and families from underserved groups."*
> — WA State Board of Education, FutureReady Interim Report, Dec 2025

---

## The Solution: PathFinder

A **multi-agent AI navigator** that takes a youth from *"I'm 17, Latina, interested in coding, South Seattle"* to a personalized 12-month roadmap — in under 10 minutes — grounded in real, live Washington state program data.

One conversation replaces 10 fragmented websites, 3 phone calls, and months of confusion.

---

## Core Features

### 1. Conversational Intake Agent
- Youth describes themselves in plain language: age, location, background, goals, constraints (childcare, income, schedule)
- No forms. No portals. Just a conversation.
- Supports English and Spanish (Sarvam AI voice layer optional)

### 2. Live WA Program Matcher
- Queries aggregated database of 47+ WA state programs: Ada Build/Core, GEAR UP, YEP, Computing for All, School's Out WA, WSAC partnerships, community college pathways
- Real-time eligibility filtering: income, age, county, demographic priority groups
- Surfaces open seats, application deadlines, required prerequisites

### 3. Personalized 12-Month Roadmap
- Step-by-step path from current skill level → first tech job or program enrollment
- Includes fallback options if primary path closes
- Benchmarked to Ada Core, community college CS, or direct-to-employment tracks

### 4. Mentor Capacity Multiplier
- AI handles 80% of repeat queries: program info, deadlines, skill gap identification
- HITL (human-in-the-loop) interrupt routes only high-complexity emotional/career pivot situations to human mentors
- 1 mentor now serves 10× the caseload

### 5. Monthly Check-In Agent
- Async SMS/WhatsApp nudges at key milestone dates
- Re-routes if a program closes or deadline passes
- Zero app install required — meets youth where they are

---

## Technical Stack

| Layer | Technology |
|---|---|
| Agent orchestration | AWS Strands + OpenClaw |
| LLM — intake + roadmap | Anthropic Claude Sonnet (Haiku for scale) |
| Voice layer (optional) | Sarvam AI (Hinglish/Spanish) |
| Program database | FastAPI + MongoDB |
| Frontend dashboard | Next.js |
| SMS/async check-ins | Twilio |
| Observability | Langfuse + OpenTelemetry |
| Deployment | GitHub Pages + EC2 |

---

## Agent Architecture

```
[Youth Input] 
    → Intake Agent (Claude Haiku)
    → Resource Matcher (OpenClaw tool — queries live WA program DB)
    → Gap Analyzer (Strands — skill gap vs. program prerequisites)
    → Roadmap Generator (Claude Sonnet — 12-month personalized path)
    → Check-In Agent (async Twilio — monthly SMS nudges)
    → Mentor Handoff (HITL interrupt — high-complexity cases only)
```

---

## State Alignment

| WA State Goal | PathFinder Alignment |
|---|---|
| FutureReady 2026 — modernize graduation for equity | Navigation layer for the programs FutureReady points to |
| WSAC: close Latino/BIPOC attainment gap (King, Pierce, Snohomish) | Primary target demographic, bilingual support |
| Ada Developers Academy — AI curriculum expansion goal | Direct feeder pipeline; Ada Build → Core pathway built in |
| School's Out WA 2023–2026 Strategic Plan | Program database includes all SOWA-affiliated afterschool programs |
| UW GEAR UP Achievers — first-gen college access | Integrated as a roadmap step for qualifying youth |

**Pitch hook**: *"Washington is rewriting graduation requirements right now. We built the navigation layer they forgot to include."*

---

## Demo Script (8-minute pitch)

1. **[0:00]** Open dashboard — show equity gap chart, 80K NEET stat
2. **[1:30]** Type: *"I'm 17, Latina, interested in coding, South Seattle"* → watch roadmap generate live
3. **[3:30]** Show Step 1: Ada Build (free, self-paced) → Step 4: Ada Core application with internship
4. **[5:00]** Show mentor dashboard: *"AI handled 47 intake queries this week. You had 3 HITL escalations."*
5. **[6:30]** Close: *"Ada has graduated 1,200 engineers. PathFinder finds the next 12,000."*

---

## GitHub Repo Structure

```
pathfinder/
├── README.md                    # Live demo link + state alignment summary
├── dashboard/                   # Next.js frontend
│   ├── components/agent/        # Conversational intake UI
│   ├── components/roadmap/      # 12-month roadmap renderer
│   ├── components/programs/     # Live WA program map + filters
│   └── components/equity/       # Gap chart + demographic data
├── api/                         # FastAPI backend
│   ├── routes/intake.py         # Agent orchestration endpoint
│   ├── routes/programs.py       # WA program DB queries
│   └── routes/checkin.py        # Twilio SMS scheduling
├── agents/
│   ├── intake_agent.py          # Strands intake agent
│   ├── resource_matcher.py      # OpenClaw tool — program eligibility
│   ├── gap_analyzer.py          # Skill gap detection
│   ├── roadmap_generator.py     # Claude Sonnet roadmap synthesis
│   └── checkin_agent.py         # Async follow-up agent
├── data/
│   ├── wa_programs.json         # 47+ WA state programs (curated)
│   ├── eligibility_rules.json   # Income/age/county filters
│   └── ada_pipeline.json        # Ada Build → Core → internship path
└── notebooks/
    └── equity_gap_analysis.ipynb  # WSAC data analysis
```

---

## Why This Wins

**For judges**: Directly aligned to Ada (co-organizer), WiT's mentorship mission, and three active WA state initiatives. The nonprofit partner can use this Monday morning.

**Technically**: Not a chatbot wrapper. A provenance-aware multi-agent system with HITL interrupt architecture — differentiates from every generic LLM submission in the room.

**Narratively**: *"1 human mentor now serves 10× the caseload"* — the WiT/Ada audience responds to capacity multiplication framing, not AI replacement framing.

---

## Post-Hackathon Path

- Deploy as Ada Developers Academy's official program navigator
- Submit to **School's Out WA** as a program discovery tool for their 2026 grantees
- Open-source the WA program database as a public resource
- EB-1A artifact: first agentic youth navigation system aligned to a state education equity mandate
