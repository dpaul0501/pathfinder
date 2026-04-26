# PathFinder — WA Youth Tech Navigator

> *"Washington has 47 free tech programs and 80,000 youth who can't find them. We built the missing link."*

---

## Inspiration

Washington state has a compounding equity crisis in tech access. The numbers are stark:

$$\text{Post-secondary attainment gap} = 62\%_{\text{statewide}} - 32\%_{\text{Latino}} = \textbf{30 points}$$

Roughly **80,000 WA youth ages 16–24** are not in education, employment, or training (NEET). Free programs exist — Ada Developers Academy, Year Up, GEAR UP, NPower, and 43 others — but they are scattered across 12 agencies, 5 nonprofits, and 3 unconnected websites.

The catalyst was a line from the WA State Board of Education's own *FutureReady 2026* interim report, published December 2025:

> *"State education policy has been developed in silos, often without sufficient input from the very communities it impacts most — students and families from underserved groups."*

Washington is rewriting graduation requirements right now. They forgot to include a navigation layer. We built it.

---

## What It Does

PathFinder is a **multi-agent AI navigator** that takes a youth from *"I'm 17, Latina, interested in coding, South Seattle"* to a personalized 12-month roadmap — grounded in real, live Washington state program data — in under 10 minutes.

### For Youth
- **Conversational intake** — no forms, no portals, just plain language
- **Live program matching** — filters 25+ verified WA programs by age, county, demographics, schedule, and income eligibility
- **Personalized micro-roadmap** — week-by-week steps from current skill level to first tech job or program enrollment
- **Mentor match** — scored by path overlap and demographic resonance; surfaces a real person who walked the same road

### Sample output for *"I'm 17, Latina, South Seattle, interested in coding"*:

| Step | Action | Program | Cost |
|---|---|---|---|
| Week 1–2 | Apply + start self-paced Python | Ada Build Self-Paced | Free |
| Week 3–4 | Complete Ada Build, apply to cohort | Ada Build Live | Free |
| Month 2 | Apply to Ada Core (deadline Jul 1) | Ada Core Cohort 22 | Tuition-free |
| Month 3 | Ada Core starts → paid internship | Amazon / Microsoft | $95K–$120K |

Mentor matched: **Sarah Reyes, SWE II at Microsoft**, Ada Core Cohort 14, South Seattle — *"I was exactly where you are."*

### For Government & Program Officers
A second tab surfaces a **live intelligence layer**:
- Real Reddit posts from youth categorized by need type, urgency, and WA location
- **Gap detection** — posts where need is urgent but no WA program exists to answer it
- **HITL dashboard** — AI-handled vs mentor-escalated cases, capacity multiplier metric
- **Theme aggregation** — top pain themes for policy prioritization

The capacity multiplier effect is meaningful. If $n$ is total cases and $h$ is HITL escalations:

$$\text{Capacity Multiplier} = \frac{n}{h}$$

In our seeded demo with 10 cases and 5 HITL: PathFinder already doubles mentor throughput. At scale across Ada's 40-mentor network, the effect compounds.

---

## How We Built It

### Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph `create_react_agent` (ReAct pattern) |
| LLM — intake + roadmap | Groq `llama-3.3-70b-versatile` (fast/free) · switchable to Claude Sonnet or GPT-4o |
| Tool 1 — Program search | Custom Python tool over curated `wa_programs.json` (25 verified programs) |
| Tool 2 — Mentor match | Scoring function: path overlap $\times 3$ + demographic resonance $\times 2$ + language match |
| Tool 3 — Reddit intel | Async `httpx` scraper → 6 subreddits → LLM categorization → gap detection |
| Backend | FastAPI + Uvicorn |
| Frontend | Vanilla HTML/CSS/JS — two-tab design (Youth / Government) |
| Gov data store | File-backed JSON with seed demo cases |

### Agent Architecture

```
[Youth Input]
    → LangGraph ReAct Agent
        → search_wa_programs(age, county, demographics, schedule)
        → match_mentor(program_ids, demographics, languages)
        → [synthesize 12-month roadmap]
    → JSON response → rendered roadmap + mentor card + job destination

[Gov Dashboard]
    → fetch_raw_posts() [async Reddit scrape, 6 subreddits]
    → categorize_posts() [LLM: need_type, urgency, location_wa]
    → detect_gaps() [unmet needs vs. program tag coverage]
    → aggregate_themes() [Counter → top 8 pain themes]
```

### Safety Design

The LLM **never generates program facts**. Every program name, deadline, eligibility rule, and seat count comes from a curated database. The model only synthesizes a roadmap *around* verified program objects. This eliminates hallucinated bootcamps and false eligibility claims — the most dangerous failure mode for a youth navigator.

HITL interrupt routes high-complexity cases (undocumented youth, foster youth needing housing, emotional distress) to human mentors. The system knows what it should not decide alone.

---

## Challenges We Ran Into

**Reddit rate limiting** — The public JSON API is sparse under load. We solved this by pre-categorizing a rich set of fallback posts with full metadata (need_type, urgency, location_wa, theme) and blending them with live data, so the government intelligence panel always shows meaningful signal even when Reddit throttles.

**JSON parsing reliability** — LangGraph's ReAct loop occasionally wraps the final response in markdown fences despite explicit prompting. We added a fence-stripping parser before `json.loads()` to handle this gracefully.

**LLM provider switching** — We needed the same agent to run on Groq (demo speed), OpenAI (judge reliability), and Anthropic Claude (production quality) without code changes. A single `LLM_PROVIDER` env var and a `_build_llm()` factory resolved this cleanly.

**Sync vs. async Reddit calls** — FastAPI is async but LangChain tools are called synchronously inside the agent loop. We used a `ThreadPoolExecutor` wrapper to call `asyncio.run()` from inside a sync context without blocking the event loop.

---

## Accomplishments That We're Proud Of

- **25 real, verified WA state programs** — every program in the database is a real program with real deadlines, real eligibility rules, and real URLs. No made-up data.
- **Sub-8-second roadmap generation** on Groq free tier — fast enough to run live in a pitch without awkward waiting.
- **Mentor matching by path overlap** — not a random match or a directory listing. Sarah Reyes appears for Marisol because Sarah actually walked Ada Build → Ada Build Live → Ada Core. The scoring function rewards that.
- **Gap detection as policy signal** — the government tab doesn't just show Reddit posts. It identifies where youth need is high and *no program exists to answer it*. That's actionable intelligence for program officers.
- **HITL escalation logic** — the system knows its own limits. Undocumented youth eligibility, housing + training combinations, and emotional complexity all route to humans.

---

## What We Learned

- **Data quality beats model quality.** The biggest improvement to roadmap accuracy came from curating the program database — not from prompt engineering. Verified facts beat clever prompts every time.
- **Government users need different UX than youth users.** A single dashboard trying to serve both audiences serves neither. The tab split was the right call — it let us optimize information density and framing for each user independently.
- **Reddit is a better policy signal than surveys.** Youth don't fill out needs assessments. They post on Reddit at 11pm when they're frustrated. Tapping that signal in near-real-time is more honest than any structured data collection.
- **The HITL framing matters.** "AI replaces mentors" loses the WiT/Ada audience immediately. "1 mentor now serves 10× the caseload" wins it. Capacity multiplication, not replacement.

---

## What's Next for PathFinder

**Immediate (post-hackathon)**
- Deploy as Ada Developers Academy's official program navigator — hand the team a working API they can embed Monday morning
- Add Sarvam AI voice layer for Spanish-language intake (bilingual support for the primary target demographic)
- SMS/WhatsApp check-in agent via Twilio — monthly milestone nudges, no app install required

**Short-term**
- Submit the WA program database as an open-source public resource — the first unified, machine-readable index of free WA youth tech programs
- Integrate real-time seat and deadline data via direct partnerships with Ada, Year Up, and NPower
- Expand Reddit intel to WSAC reports, OSPI data, and LinkedIn job postings for richer policy signal

**Long-term**
- Partner with School's Out WA as a program discovery tool for their 2026 grantee network (200+ afterschool sites)
- Build the policy gap report into a quarterly brief for WA legislators — automated, sourced, actionable
- EB-1A artifact: first agentic youth navigation system aligned to an active state education equity mandate

$$\text{Ada graduated } 1{,}200 \text{ engineers.} \quad \text{PathFinder finds the next } 12{,}000.$$

---

## Built With

`python` `fastapi` `langgraph` `langchain` `groq` `anthropic-claude` `openai` `httpx` `pydantic` `uvicorn` `javascript` `html` `css` `python-dotenv` `reddit-api`
