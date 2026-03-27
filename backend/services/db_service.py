"""Database service — saves and retrieves simulation results from Supabase."""

import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_client = None


def _get_client():
    """Lazy-initialize the Supabase client."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return None
        from supabase import create_client
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def save_simulation(sim_id: str, zip_code: str, policy: str, results: dict) -> bool:
    """Save a completed simulation to Supabase. Returns True on success."""
    client = _get_client()
    if not client:
        return False

    summary = results.get("summary", {})
    try:
        client.table("simulations").insert({
            "id": sim_id,
            "zip_code": zip_code,
            "policy": policy,
            "support_pct": summary.get("support_pct", 0),
            "oppose_pct": summary.get("oppose_pct", 0),
            "num_personas": summary.get("total_personas", 0),
            "results": json.dumps(results),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Failed to save simulation to Supabase: {e}")
        return False


def list_simulations(limit: int = 50) -> list[dict]:
    """List past simulations, most recent first."""
    client = _get_client()
    if not client:
        return []

    try:
        response = (
            client.table("simulations")
            .select("id, zip_code, policy, support_pct, oppose_pct, num_personas, created_at")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Failed to list simulations from Supabase: {e}")
        return []


def get_simulation(sim_id: str) -> dict | None:
    """Retrieve a specific simulation's full results."""
    client = _get_client()
    if not client:
        return None

    try:
        response = (
            client.table("simulations")
            .select("*")
            .eq("id", sim_id)
            .single()
            .execute()
        )
        row = response.data
        if row and row.get("results"):
            row["results"] = json.loads(row["results"])
        return row
    except Exception as e:
        print(f"Failed to get simulation from Supabase: {e}")
        return None
