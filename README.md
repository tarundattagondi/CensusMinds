# CensusMinds

**Census-grounded local policy impact simulator** — 100 AI personas from real US Census data predict how your community will react to proposed policies.

## What It Does

CensusMinds pulls real demographic data from the US Census Bureau for any ZIP code and generates a statistically accurate population of AI personas. Each persona evaluates a proposed local policy through the lens of their income, housing, commute, education, and life circumstances — surfacing support/opposition breakdowns, hidden impacts on underrepresented groups, and community-driven modification suggestions.

## How It Works

1. **Enter a ZIP code and policy** — e.g., "Remove 200 parking spots for bike lanes"
2. **Census data is fetched** — real demographics from ACS 5-Year profiles (age, income, race, education, housing, commute, vehicles)
3. **Personas are generated** — 100 residents created via weighted random sampling to match the ZIP's actual distributions
4. **AI simulates each persona** — Claude evaluates the policy in character, producing a stance, impact rating, reasoning, and suggestions
5. **Results are aggregated** — support/oppose breakdowns by demographic group, hidden impacts, top concerns, and modification ideas

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Census Data | [US Census Bureau ACS 5-Year API](https://www.census.gov/data/developers/data-sets/acs-5year.html) |
| AI Simulation | [Anthropic Claude API](https://docs.anthropic.com/) (claude-sonnet-4-20250514) |
| HTTP Client | [httpx](https://www.python-httpx.org/) (async) |
| PDF Export | [ReportLab](https://www.reportlab.com/) |
| Frontend | [React](https://react.dev/) + [Vite](https://vite.dev/) |
| Charts | [Recharts](https://recharts.org/) |
| Styling | [Tailwind CSS](https://tailwindcss.com/) |
| Database | [Supabase](https://supabase.com/) (planned) |
| Language | Python 3.11+ / JavaScript (ES2022) |

## Setup

```bash
# Clone the repo
git clone https://github.com/tarundattagondi/CensusMinds.git
cd CensusMinds

# Create virtual environment and install backend dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   CENSUS_API_KEY    — get one at https://api.census.gov/data/key_signup.html (optional, works without)
#   ANTHROPIC_API_KEY — get one at https://console.anthropic.com/
#   SUPABASE_URL      — from your Supabase project settings (optional)
#   SUPABASE_KEY      — from your Supabase project settings (optional)
```

## Running the App

**Option 1: Run script (both servers at once)**
```bash
./run.sh
```

**Option 2: Run separately**
```bash
# Terminal 1 — Backend
source .venv/bin/activate
uvicorn backend.app:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## Demo Mode

Don't have API keys? Try the demo mode which uses pre-loaded simulation results — no API calls needed.

- **Frontend:** Click "or try a demo with pre-loaded results" on the landing page
- **API:** `POST /api/simulate?demo=true` with any request body

Demo uses ZIP 22030 (Fairfax, VA) with a bike lane policy and 20 pre-computed persona responses.

## API Endpoints

### `GET /`
Health check. Returns `{"status": "healthy", "service": "CensusMinds API"}`.

### `GET /api/census/{zip_code}`
Fetch cached census demographics for a ZIP code.

**Example:** `GET /api/census/22030`

### `POST /api/simulate`
Start a new policy simulation. Runs in the background and returns a simulation ID.

**Query params:** `?demo=true` to use pre-loaded demo results.

**Request body:**
```json
{
  "zip_code": "22030",
  "policy_description": "Remove 200 street parking spots to add protected bike lanes on Main Street",
  "num_personas": 100
}
```

**Response:**
```json
{
  "sim_id": "uuid-here",
  "status": "pending"
}
```

### `GET /api/simulate/{sim_id}/status`
Poll simulation progress. Returns status (`pending`, `fetching_census`, `generating_personas`, `running_simulation`, `aggregating`, `complete`, `error`), progress (0-100), and full results when complete.

### `GET /api/simulate/{sim_id}/export`
Download simulation results as a PDF report.

## Running Tests

```bash
# Test census data fetch + persona generation
python backend/tests/test_census.py

# Full end-to-end simulation (requires ANTHROPIC_API_KEY)
python backend/tests/test_full_simulation.py
```

## Example Output

<!-- Add screenshots here -->
*Screenshots placeholder — run the app or use demo mode to see the full dashboard*

## License

MIT

## Built With

Census API | Claude API | FastAPI | React | Recharts | Tailwind CSS | ReportLab

## Built By

**Tarun Datta Gondi**
