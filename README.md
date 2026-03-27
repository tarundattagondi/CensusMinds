# CensusMinds

### What does your community *actually* think?

A census-grounded local policy impact simulator that generates 100 AI personas from real US Census data to predict community reactions to proposed policies.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## The Problem

When cities propose policy changes, only the loudest voices show up at public meetings. The single parent working nights, the elderly resident on a fixed income, the student renting a room downtown -- they never get heard. Decisions get made based on a skewed sample of the population, without understanding who actually gets hurt and who benefits.

CensusMinds fills that gap by simulating how a statistically representative population would actually react to a proposed policy.

## How It Works

1. **Enter a ZIP code** -- the app fetches real demographic data from the US Census Bureau ACS 5-Year API
2. **100 unique AI personas are generated** -- each with a name, age, income, job, housing, commute mode, education, ethnicity, and personality traits, statistically matching the ZIP code's actual population
3. **Each persona reacts to the proposed policy** -- stating support or opposition, impact level, reasoning, and a suggested modification
4. **Results are aggregated into an interactive dashboard** -- with demographic breakdowns, hidden impact detection, and individual persona stories

---

## Live Demo

| | URL |
|---|-----|
| **App** | [census-minds.vercel.app](https://census-minds.vercel.app) |
| **Backend API** | [web-production-a61c.up.railway.app](https://web-production-a61c.up.railway.app) |

Demo mode is available on the landing page -- try the full dashboard without any API keys.

---

## Key Features

- [x] **Real Census Data** -- demographics pulled directly from US Census Bureau ACS 5-Year Estimates (DP02, DP03, DP04, DP05 profile tables)
- [x] **100 AI Personas** -- statistically representative of actual ZIP code population via weighted random sampling
- [x] **Demographic Breakdowns** -- support/oppose split by income, age, commute mode, housing type, education, and ethnicity
- [x] **Hidden Impact Detection** -- identifies groups with HIGH/CRITICAL impact but low likelihood of attending public meetings
- [x] **Individual Persona Stories** -- read each persona's unique reasoning, impact assessment, and suggested policy modifications
- [x] **Rate Limiting** -- 2 free simulations per day
- [x] **Bring Your Own Key** -- paste your own Anthropic API key for unlimited simulations
- [x] **Download Results** -- export full simulation results as a styled PDF report or CSV data file
- [x] **Simulation History** -- save, browse, and revisit past simulation results
- [x] **Demo Mode** -- pre-loaded results for ZIP 22030 (Fairfax, VA) to explore the full dashboard without API costs

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python, FastAPI, Uvicorn, httpx, ReportLab |
| **AI** | Anthropic Claude API |
| **Data** | US Census Bureau ACS 5-Year Profile API |
| **Frontend** | React, Vite, Tailwind CSS, Recharts |
| **Database** | Supabase (PostgreSQL) |
| **Deployment** | Vercel (frontend), Railway (backend) |

---

## Screenshots

> Screenshots coming soon.

| Landing Page | Results Dashboard |
|:---:|:---:|
| *Policy input form with ZIP code entry* | *Support/oppose gauge with demographic breakdowns* |

| Persona Cards | Demographic Charts |
|:---:|:---:|
| *Individual persona responses with reasoning* | *Bar charts showing breakdown by income and age* |

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Census API key ([get one here](https://api.census.gov/data/key_signup.html)) -- optional, the app works without one

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

Edit `.env` and add your keys:

```
CENSUS_API_KEY=your_census_key_here        # Optional
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
# Terminal 1 -- Backend (port 8000)
source .venv/bin/activate
uvicorn backend.app:app --reload --port 8000

# Terminal 2 -- Frontend (port 5173)
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Running Tests

```bash
# Census data fetch + persona generation (no API key needed)
python backend/tests/test_census.py

# Full end-to-end simulation (requires ANTHROPIC_API_KEY)
python backend/tests/test_full_simulation.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/simulate` | Run a new policy simulation (accepts `?demo=true`) |
| `GET` | `/api/simulations` | List all past simulations |
| `GET` | `/api/simulations/:id` | Get full saved simulation results |
| `GET` | `/api/census/:zip` | Fetch census demographics for a ZIP code |
| `GET` | `/api/export/:id/pdf` | Download simulation results as PDF |
| `GET` | `/api/export/:id/csv` | Download persona responses as CSV |

---

## Cost

| Item | Cost |
|------|------|
| Hosting (Vercel + Railway free tiers) | Free |
| Census API | Free |
| Per simulation (100 personas) | ~$0.09 - $0.50 |
| Demo mode | Free |
| Viewing past results | Free |
| PDF/CSV downloads | Free |

---

## Who This Helps

- **City council members** evaluating proposed ordinances before public comment periods
- **Urban planners** assessing community impact of infrastructure and zoning changes
- **Journalists** investigating which populations a policy would disproportionately affect
- **Community organizers** building targeted outreach strategies for underrepresented groups
- **Public policy students** studying how demographic composition shapes policy preferences
- **Civic tech nonprofits** developing tools for more inclusive public engagement

---

## What Makes This Unique

Existing multi-agent simulation tools focus on marketing personas (Synthetic Users), academic social science research (Stanford Generative Agents), or abstract agent-based modeling (AgentSociety). None of them connect LLM-powered agent simulation to **real, ground-truth demographic data** for **civic policy prediction**.

CensusMinds is the first tool to:

- Ground every persona in **real US Census Bureau data** for a specific ZIP code
- Use **weighted random sampling** so the simulated population statistically mirrors the actual community
- Focus specifically on **local policy impact** rather than consumer behavior or academic experiments
- Surface **hidden impacts** -- identifying which demographic groups are most affected but least likely to participate in traditional public engagement
- Make results **actionable** for real decision-makers through demographic breakdowns, exportable reports, and specific modification suggestions

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Built By

**Tarun Datta Gondi**
MS Computer Science, George Mason University
[github.com/tarundattagondi](https://github.com/tarundattagondi)
