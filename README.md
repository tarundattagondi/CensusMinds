# CensusMinds

### What does your community *actually* think?

A census-grounded local policy impact simulator that generates 100 AI personas from real US Census data to predict community reactions to proposed policies.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat&logo=fastapi&logoColor=white)
![Claude API](https://img.shields.io/badge/Claude_API-Sonnet_4-D97757?style=flat&logo=anthropic&logoColor=white)
![Census API](https://img.shields.io/badge/US_Census-ACS_5--Year-003366?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## The Problem

When cities propose policy changes, only the loudest voices show up at public meetings. The single parent working nights, the elderly resident on a fixed income, the student renting a room downtown — they never get heard. Decisions get made based on a skewed sample of the population, without understanding who actually gets hurt and who benefits.

Public comment periods and town halls systematically underrepresent low-income residents, renters, shift workers, non-English speakers, and young people. The result: policies pass with blind spots that disproportionately impact the people least likely to show up.

## What CensusMinds Does

CensusMinds bridges the gap between policy proposals and community impact by simulating how a statistically representative population would actually react:

1. **Enter a ZIP code and a policy description** (e.g., "Remove 200 parking spots for protected bike lanes")
2. The app fetches **real demographic data** from the US Census Bureau ACS 5-Year API for that ZIP code
3. It generates **100 unique AI personas** — each with a name, age, income, job, housing situation, commute mode, education level, ethnicity, and personality traits — statistically matching the ZIP code's actual population distributions
4. Each persona **evaluates the policy through Claude AI**, stating whether they support or oppose it, rating the impact on their life, explaining their reasoning, and suggesting modifications
5. Results are **aggregated into an interactive dashboard** with demographic breakdowns, hidden impact detection, and individual persona stories

---

## Key Features

- [x] **Real Census Data** — Demographics pulled directly from US Census Bureau ACS 5-Year Estimates (DP02, DP03, DP04, DP05 profile tables)
- [x] **100 AI Personas** — Statistically representative of actual ZIP code population via weighted random sampling
- [x] **Demographic Breakdowns** — Support/oppose split by income bracket, age group, commute mode, housing type, education, and ethnicity
- [x] **Hidden Impact Detection** — Identifies groups with HIGH/CRITICAL impact but low likelihood of attending public meetings
- [x] **Individual Persona Stories** — Read each persona's unique reasoning, impact assessment, and suggested policy modifications
- [x] **Rate Limiting** — 5 free simulations per day using the server's Anthropic API key
- [x] **Bring Your Own Key** — Users can paste their own Anthropic API key for unlimited simulations
- [x] **Download Results** — Export full simulation results as a styled PDF report or CSV data file
- [x] **Simulation History** — Save, browse, and revisit past simulation results
- [x] **Demo Mode** — Pre-loaded results for ZIP 22030 (Fairfax, VA) to explore the full dashboard without API costs

---

## How It Works

### Step 1: Enter ZIP Code
The user enters a 5-digit ZIP code. CensusMinds fetches real demographic data from the US Census Bureau ACS 5-Year API, pulling age distribution, race/ethnicity, income brackets, education levels, commute modes, housing tenure, vehicles per household, and household types.

### Step 2: Generate Personas
Using weighted random sampling, the system generates 100 personas whose collective demographics match the real population. Each persona gets a culturally appropriate name, a job title matching their education level, and 2-3 personality traits that influence their policy perspective.

### Step 3: Simulate Reactions
Each persona is sent to Claude AI with their full demographic profile as context. The LLM responds in character with: a stance (SUPPORT/OPPOSE), an impact level (NONE through CRITICAL), 2-3 sentences of reasoning, whether they would attend a public meeting, and one suggested modification to the policy.

### Step 4: View Results
The interactive dashboard displays support/oppose percentages, demographic breakdowns via bar charts, hidden impact alerts for underrepresented groups, top concerns and benefits extracted from reasoning text, and scrollable cards showing every persona's individual response.

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn, httpx (async), ReportLab (PDF generation) |
| **AI** | Anthropic Claude API (claude-sonnet-4-20250514) |
| **Data** | US Census Bureau ACS 5-Year Profile API |
| **Frontend** | React 19, Vite, Tailwind CSS, Recharts |
| **Storage** | Local JSON / Supabase (PostgreSQL) |
| **Deployment** | Vercel (frontend), Railway (backend) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/simulate` | Run a new policy simulation (accepts `?demo=true`) |
| `GET` | `/api/simulate/{sim_id}/status` | Poll simulation progress (0-100%) |
| `GET` | `/api/simulations` | List all past simulations |
| `GET` | `/api/simulations/{sim_id}` | Get full saved simulation results |
| `GET` | `/api/census/{zip_code}` | Fetch census demographics for a ZIP code |
| `GET` | `/api/export/{sim_id}/pdf` | Download simulation results as PDF |
| `GET` | `/api/export/{sim_id}/csv` | Download persona responses as CSV |
| `GET` | `/api/rate-limit` | Check remaining daily simulations |
| `GET` | `/` | Health check |

**Example request:**

```bash
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "zip_code": "22030",
    "policy_description": "Remove 200 street parking spots to add protected bike lanes",
    "num_personas": 100,
    "anthropic_api_key": "sk-ant-..."
  }'
```

---

## Project Structure

```
CensusMinds/
├── backend/
│   ├── app.py                          # FastAPI application and routes
│   ├── config.py                       # Environment variable loader
│   ├── data/
│   │   ├── demo_simulation.json        # Pre-loaded demo results
│   │   ├── names.json                  # Names by ethnicity for persona generation
│   │   ├── jobs.json                   # Job titles by education level
│   │   └── schema.sql                  # Supabase table schema
│   ├── services/
│   │   ├── census_service.py           # US Census ACS API integration
│   │   ├── persona_generator.py        # Weighted random persona generation
│   │   ├── llm_service.py             # Claude API simulation engine
│   │   ├── aggregator.py              # Results aggregation and analysis
│   │   ├── export_service.py          # PDF and CSV report generation
│   │   └── db_service.py             # Simulation storage (JSON/Supabase)
│   └── tests/
│       ├── test_census.py             # Census + persona generation test
│       └── test_full_simulation.py    # End-to-end simulation test
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # React Router configuration
│   │   ├── pages/
│   │   │   ├── Landing.jsx            # Home page with policy input form
│   │   │   ├── Loading.jsx            # Simulation progress screen
│   │   │   ├── Results.jsx            # Interactive results dashboard
│   │   │   └── History.jsx            # Past simulations browser
│   │   └── services/
│   │       └── api.js                 # Backend API client (axios)
│   └── vite.config.js                 # Vite + Tailwind configuration
├── .env.example                        # Environment variable template
├── requirements.txt                    # Python dependencies
├── run.sh                              # Start both servers
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Census API key ([get one here](https://api.census.gov/data/key_signup.html)) — optional, works without one

### Installation

```bash
# Clone the repository
git clone https://github.com/tarundattagondi/CensusMinds.git
cd CensusMinds

# Set up the backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set up the frontend
cd frontend
npm install
cd ..

# Configure environment variables
cp .env.example .env
```

Edit `.env` and add your API keys:

```
CENSUS_API_KEY=your_census_key_here        # Optional — works without it
ANTHROPIC_API_KEY=sk-ant-api03-...         # Required for real simulations
SUPABASE_URL=https://your-project.supabase.co   # Optional
SUPABASE_KEY=your_supabase_key             # Optional
```

### Running

**Option 1: Both servers at once**

```bash
./run.sh
```

**Option 2: Separately**

```bash
# Terminal 1 — Backend (port 8000)
source .venv/bin/activate
uvicorn backend.app:app --reload --port 8000

# Terminal 2 — Frontend (port 5173)
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### Running Tests

```bash
# Test census data fetch + persona generation (no API key needed)
python backend/tests/test_census.py

# Full end-to-end simulation (requires ANTHROPIC_API_KEY)
python backend/tests/test_full_simulation.py
```

---

## Cost Breakdown

| Item | Cost |
|------|------|
| Hosting (Vercel + Railway free tier) | Free |
| US Census Bureau API | Free |
| Claude API per simulation (100 personas) | ~$0.09 - $0.50 |
| Demo mode | Free |
| Viewing past results | Free |
| PDF/CSV downloads | Free |

---

## What Makes This Unique

Existing multi-agent simulation tools focus on marketing personas (Synthetic Users), academic social science research (Stanford Generative Agents), or abstract agent-based modeling (AgentSociety). None of them connect LLM-powered agent simulation to **real, ground-truth demographic data** for **civic policy prediction**.

CensusMinds is the first tool to:

- Ground every persona in **real US Census Bureau data** for a specific ZIP code
- Use **weighted random sampling** so the simulated population statistically mirrors the actual community
- Focus specifically on **local policy impact** rather than consumer behavior or academic experiments
- Surface **hidden impacts** — identifying which demographic groups are most affected but least likely to participate in traditional public engagement
- Make results **actionable** for real decision-makers through demographic breakdowns, exportable reports, and specific modification suggestions

---

## Who This Helps

- **City council members** evaluating proposed ordinances before public comment periods
- **Urban planners** assessing community impact of infrastructure and zoning changes
- **Journalists** investigating which populations a policy would disproportionately affect
- **Community organizers** building targeted outreach strategies for underrepresented groups
- **Public policy students** studying how demographic composition shapes policy preferences
- **Civic tech nonprofits** developing tools for more inclusive public engagement

---

## Built By

**Tarun Datta Gondi**
MS Computer Science, George Mason University
GitHub: [tarundattagondi](https://github.com/tarundattagondi)

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
