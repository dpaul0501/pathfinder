# PathFinder — WA Youth Tech Navigator

> *One conversation. One roadmap. Under 10 minutes.*

Built at **HSI × WiT Regatta Hackathon 2026** · Track: Youth Empowerment · AI House, Seattle

---

## The Problem

Washington state has 47 free tech programs for under-resourced youth — scattered across 12 agencies, 5 nonprofits, and 3 unconnected websites. ~80,000 WA youth ages 16–24 are not in education, employment, or training. The pipeline exists. Youth can't find it.

## What It Does

PathFinder is a multi-agent AI navigator. A youth types one sentence — *"I'm 17, Latina, interested in coding, South Seattle"* — and gets back:

- A **personalized 12-month roadmap** through verified, free WA state programs
- A **mentor match** scored by path overlap and demographic resonance
- A **job destination** with salary range and realistic timeline

A second tab gives program officers and policymakers a **live government intelligence layer** — real Reddit signal, unmet-need gap detection, and a HITL mentor capacity dashboard.

---

## Stack

| Layer | Tech |
|---|---|
| Agent | LangGraph ReAct · `create_react_agent` |
| LLM | Groq `llama-3.3-70b` · switchable to Claude / GPT-4o |
| Backend | FastAPI + Uvicorn |
| Tools | Program search · Mentor match · Reddit intel |
| Frontend | Vanilla HTML/CSS/JS — two-tab (Youth / Government) |
| Reddit | Async `httpx` scraper → LLM categorization → gap detection |

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/dpaul0501/pathfinder.git
cd pathfinder

# 2. Virtual environment
python3 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Environment variables
cp .env.example .env   # add your GROQ_API_KEY (free at console.groq.com)

# 4. Run backend
uvicorn backend.main:app --port 8001 --reload

# 5. Open frontend
python3 -m http.server 5050
# → http://localhost:5050/pathfinder_dashboard.html
```

### Environment Variables

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | `groq` (default) · `openai` · `anthropic` |
| `GROQ_API_KEY` | Free at console.groq.com |
| `OPENAI_API_KEY` | Optional — for GPT-4o demo mode |
| `ANTHROPIC_API_KEY` | Optional — for Claude production mode |

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/navigate` | POST | Youth message → personalized roadmap JSON |
| `/api/programs` | GET | All 25 WA programs |
| `/api/gov/intel` | GET | Reddit signal · gaps · themes |
| `/api/gov/mentor/stats` | GET | AI handled vs HITL · capacity multiplier |
| `/api/gov/mentor/cases` | GET | Recent case log |
| `/api/gov/mentor/feedback` | POST | Log a new mentor case |

---

## Agent Architecture

```
[Youth Input]
    → LangGraph ReAct Agent
        → search_wa_programs(age, county, demographics, schedule)
        → match_mentor(program_ids, demographics, languages)
        → synthesize 12-month roadmap
    → JSON → roadmap + mentor card + job destination

[Gov Dashboard]
    → fetch_raw_posts()       # async Reddit scrape, 6 subreddits
    → categorize_posts()      # LLM: need_type, urgency, location_wa
    → detect_gaps()           # unmet needs vs. program coverage
    → aggregate_themes()      # top pain themes for policy
```

**Safety:** The LLM never generates program facts. All names, deadlines, eligibility rules, and seat counts come from a curated database. The model only synthesizes a roadmap around verified program objects.

---

## WA State Alignment

| Initiative | PathFinder Role |
|---|---|
| FutureReady 2026 | Navigation layer for the programs FutureReady points to |
| WSAC Latino/BIPOC attainment gap | Primary target demographic, bilingual roadmap support |
| Ada Developers Academy | Direct feeder pipeline — Ada Build → Core built in |
| School's Out WA 2026 | Program database includes all SOWA-affiliated programs |
| UW GEAR UP | Integrated as a roadmap step for qualifying youth |

---

## Repo Structure

```
pathfinder/
├── pathfinder_dashboard.html     # Frontend — two-tab UI
├── PathFinder_Pitch_Deck.pptx    # 4-slide pitch deck
├── backend/
│   ├── main.py                   # FastAPI app
│   ├── agents/graph.py           # LangGraph ReAct agent
│   ├── tools/
│   │   ├── program_search.py     # WA program filter
│   │   ├── mentor_match.py       # Mentor scoring
│   │   ├── reddit_intel.py       # Advanced Reddit + LLM categorization
│   │   └── reddit_pain.py        # Simple Reddit scraper
│   ├── routes/gov.py             # Government intelligence API
│   ├── core/mentor_store.py      # HITL case log
│   └── data/
│       ├── wa_programs.json      # 25 verified WA programs
│       └── mentors.json          # 5 mentor profiles
└── build_deck.py                 # PPTX generator (python-pptx)
```

---

## Built With

`python` · `fastapi` · `langgraph` · `langchain` · `groq` · `anthropic-claude` · `openai` · `httpx` · `pydantic` · `uvicorn` · `javascript` · `html` · `css` · `reddit-api`

---

*HSI × WiT Regatta Hackathon 2026 · Built by Deb Paul*
