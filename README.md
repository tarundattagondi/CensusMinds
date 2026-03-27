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
| Backend API | FastAPI + Uvicorn |
| Census Data | US Census Bureau ACS 5-Year API |
| AI Simulation | Anthropic Claude API (claude-sonnet-4-20250514) |
| HTTP Client | httpx (async) |
| Database | Supabase (planned) |
| Frontend | React (planned) |
| Language | Python 3.11+ |

## Setup

```bash
# Clone the repo
git clone https://github.com/tarundattagondi/CensusMinds.git
cd CensusMinds

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   CENSUS_API_KEY    — get one at https://api.census.gov/data/key_signup.html (optional, works without)
#   ANTHROPIC_API_KEY — get one at https://console.anthropic.com/
#   SUPABASE_URL      — from your Supabase project settings
#   SUPABASE_KEY      — from your Supabase project settings

# Run the API server
uvicorn backend.app:app --reload
```

## API Endpoints

### `GET /`
Health check. Returns `{"status": "healthy", "service": "CensusMinds API"}`.

### `GET /api/census/{zip_code}`
Fetch cached census demographics for a ZIP code.

**Example:** `GET /api/census/22030`

### `POST /api/simulate`
Start a new policy simulation. Runs in the background and returns a simulation ID.

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

**Example response (complete):**
```json
{
  "id": "uuid-here",
  "status": "complete",
  "progress": 100,
  "results": {
    "summary": {
      "support_pct": 72.0,
      "oppose_pct": 28.0
    },
    "breakdown_by_income": { "...": "..." },
    "breakdown_by_age_group": { "...": "..." },
    "hidden_impacts": [ "..." ],
    "top_concerns": [ "..." ],
    "top_benefits": [ "..." ],
    "suggested_modifications": [ "..." ]
  }
}
```

## Running Tests

```bash
# Test census data fetch + persona generation
python backend/tests/test_census.py

# Full end-to-end simulation (requires ANTHROPIC_API_KEY)
python backend/tests/test_full_simulation.py
```

## Example Output

<!-- Add screenshot here -->
*Screenshot placeholder — run the end-to-end test to see full output*

## License

MIT

## Built By

**Tarun Datta Gondi**
