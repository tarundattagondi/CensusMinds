"""CensusMinds API — FastAPI application for census-grounded policy simulation."""

import uuid
import json
import asyncio
from datetime import date
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.services.census_service import fetch_demographics
from backend.services.persona_generator import generate_personas
from backend.services.llm_service import simulate_batch
from backend.services.aggregator import aggregate_results
from backend.services.export_service import generate_pdf, generate_csv
from backend.services.db_service import save_simulation, list_simulations, get_simulation

app = FastAPI(
    title="CensusMinds",
    description="Census-grounded local policy impact simulator",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://census-minds.vercel.app",
        "https://census-minds-tarundattagondis-projects.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores
census_cache: dict[str, dict] = {}
simulations: dict[str, dict] = {}

# Rate limiting
DAILY_LIMIT = 5
RATE_LIMIT_FILE = Path(__file__).resolve().parent / "data" / "rate_limit.json"


def _get_rate_limit() -> dict:
    """Read the current rate limit state from disk."""
    if RATE_LIMIT_FILE.exists():
        with open(RATE_LIMIT_FILE) as f:
            data = json.load(f)
        if data.get("date") == str(date.today()):
            return data
    return {"date": str(date.today()), "count": 0}


def _increment_rate_limit():
    """Increment the daily simulation counter."""
    data = _get_rate_limit()
    data["count"] += 1
    with open(RATE_LIMIT_FILE, "w") as f:
        json.dump(data, f)


def _remaining_simulations() -> int:
    """Return how many free simulations are left today."""
    data = _get_rate_limit()
    return max(0, DAILY_LIMIT - data["count"])


class SimulationRequest(BaseModel):
    zip_code: str
    policy_description: str
    num_personas: int = Field(default=100, ge=1, le=500)
    anthropic_api_key: str | None = Field(default=None, description="Optional user-provided Anthropic API key")


@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "CensusMinds API"}


@app.get("/api/rate-limit")
async def get_rate_limit():
    """Return remaining daily simulations."""
    remaining = _remaining_simulations()
    return {"remaining": remaining, "limit": DAILY_LIMIT, "date": str(date.today())}


@app.get("/api/census/{zip_code}")
async def get_census_data(zip_code: str):
    """Fetch and cache census data for a ZIP code."""
    if zip_code in census_cache:
        return census_cache[zip_code]

    try:
        data = await fetch_demographics(zip_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch census data: {str(e)}")

    census_cache[zip_code] = data
    return data


@app.get("/api/simulations")
async def get_simulations_history():
    """List all past simulations from the database."""
    return list_simulations()


@app.get("/api/simulations/{sim_id}")
async def get_saved_simulation(sim_id: str):
    """Retrieve a saved simulation's full results from the database."""
    # Check in-memory first
    if sim_id in simulations and simulations[sim_id]["status"] == "complete":
        return simulations[sim_id]

    # Check database
    row = get_simulation(sim_id)
    if not row:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # Reconstruct the simulation object for the frontend
    return {
        "id": row["id"],
        "status": "complete",
        "zip_code": row["zip_code"],
        "policy": row["policy"],
        "num_personas": row.get("num_personas", 0),
        "progress": 100,
        "results": row["results"],
        "error": None,
    }


@app.post("/api/simulate")
async def create_simulation(req: SimulationRequest, background_tasks: BackgroundTasks, demo: bool = Query(default=False)):
    """Start a new policy simulation. Use ?demo=true to load pre-computed demo results."""
    sim_id = str(uuid.uuid4())

    if demo:
        demo_path = Path(__file__).resolve().parent / "data" / "demo_simulation.json"
        with open(demo_path) as f:
            demo_results = json.load(f)
        simulations[sim_id] = {
            "id": sim_id,
            "status": "complete",
            "zip_code": demo_results["zip_code"],
            "policy": demo_results["policy"],
            "num_personas": demo_results["summary"]["total_personas"],
            "progress": 100,
            "results": demo_results,
            "error": None,
        }
        save_simulation(sim_id, demo_results["zip_code"], demo_results["policy"], demo_results)
        return {"sim_id": sim_id, "status": "complete"}

    # Check rate limit (skip if user provides their own key)
    user_key = req.anthropic_api_key
    if not user_key:
        remaining = _remaining_simulations()
        if remaining <= 0:
            raise HTTPException(
                status_code=429,
                detail="Daily simulation limit reached. Please use demo mode or provide your own Anthropic API key.",
            )
        _increment_rate_limit()

    simulations[sim_id] = {
        "id": sim_id,
        "status": "pending",
        "zip_code": req.zip_code,
        "policy": req.policy_description,
        "num_personas": req.num_personas,
        "progress": 0,
        "results": None,
        "error": None,
    }

    background_tasks.add_task(_run_simulation, sim_id, req.zip_code, req.policy_description, req.num_personas, user_key)
    return {"sim_id": sim_id, "status": "pending", "remaining": _remaining_simulations()}


@app.get("/api/simulate/{sim_id}/status")
async def get_simulation_status(sim_id: str):
    """Check the status of a running simulation."""
    if sim_id not in simulations:
        # Try loading from database
        row = get_simulation(sim_id)
        if row:
            simulations[sim_id] = {
                "id": row["id"],
                "status": "complete",
                "zip_code": row["zip_code"],
                "policy": row["policy"],
                "num_personas": row.get("num_personas", 0),
                "progress": 100,
                "results": row["results"],
                "error": None,
            }
            return simulations[sim_id]
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulations[sim_id]


@app.get("/api/export/{sim_id}/pdf")
async def export_simulation_pdf(sim_id: str):
    """Export simulation results as a PDF report."""
    sim = await _get_complete_sim(sim_id)
    pdf_bytes = generate_pdf(sim["results"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=censusminds_{sim_id[:8]}.pdf"},
    )


@app.get("/api/export/{sim_id}/csv")
async def export_simulation_csv(sim_id: str):
    """Export all persona responses as a CSV file."""
    sim = await _get_complete_sim(sim_id)
    csv_str = generate_csv(sim["results"])
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=censusminds_{sim_id[:8]}.csv"},
    )


async def _get_complete_sim(sim_id: str) -> dict:
    """Get a complete simulation from memory or database."""
    if sim_id in simulations:
        sim = simulations[sim_id]
        if sim["status"] == "complete":
            return sim

    row = get_simulation(sim_id)
    if row:
        return {
            "id": row["id"],
            "status": "complete",
            "results": row["results"],
        }

    raise HTTPException(status_code=404, detail="Simulation not found or not yet complete")


async def _run_simulation(sim_id: str, zip_code: str, policy: str, num_personas: int, api_key: str | None = None):
    """Background task that runs the full simulation pipeline."""
    sim = simulations[sim_id]
    try:
        # Step 1: Fetch census data
        sim["status"] = "fetching_census"
        sim["progress"] = 10
        if zip_code in census_cache:
            census_data = census_cache[zip_code]
        else:
            census_data = await fetch_demographics(zip_code)
            census_cache[zip_code] = census_data

        # Step 2: Generate personas
        sim["status"] = "generating_personas"
        sim["progress"] = 25
        personas = generate_personas(census_data, n=num_personas)

        # Step 3: Run LLM simulation
        sim["status"] = "running_simulation"
        sim["progress"] = 40
        responses = await simulate_batch(personas, policy, batch_size=10, api_key=api_key)
        sim["progress"] = 85

        # Step 4: Aggregate results
        sim["status"] = "aggregating"
        sim["progress"] = 90
        results = aggregate_results(responses)
        results["zip_code"] = zip_code
        results["policy"] = policy
        results["census_snapshot"] = {
            "total_population": census_data["total_population"],
            "median_household_income": census_data["median_household_income"],
        }

        sim["status"] = "complete"
        sim["progress"] = 100
        sim["results"] = results

        # Step 5: Save to database
        save_simulation(sim_id, zip_code, policy, results)

    except Exception as e:
        sim["status"] = "error"
        sim["error"] = str(e)
