"""Database service — saves and retrieves simulation results using local JSON storage."""

import json
from datetime import datetime, timezone
from pathlib import Path

STORAGE_FILE = Path(__file__).resolve().parent.parent / "data" / "simulations.json"


def _read_store() -> list[dict]:
    """Read all simulations from the local JSON file."""
    if not STORAGE_FILE.exists():
        return []
    with open(STORAGE_FILE) as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []


def _write_store(data: list[dict]):
    """Write all simulations to the local JSON file."""
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def save_simulation(sim_id: str, zip_code: str, policy: str, results: dict) -> bool:
    """Save a completed simulation. Returns True on success."""
    summary = results.get("summary", {})
    store = _read_store()

    # Don't save duplicates
    if any(s["id"] == sim_id for s in store):
        return True

    store.insert(0, {
        "id": sim_id,
        "zip_code": zip_code,
        "policy": policy,
        "support_pct": summary.get("support_pct", 0),
        "oppose_pct": summary.get("oppose_pct", 0),
        "num_personas": summary.get("total_personas", 0),
        "results": results,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    _write_store(store)
    return True


def list_simulations(limit: int = 50) -> list[dict]:
    """List past simulations (without full results), most recent first."""
    store = _read_store()
    out = []
    for s in store[:limit]:
        out.append({
            "id": s["id"],
            "zip_code": s["zip_code"],
            "policy": s["policy"],
            "support_pct": s.get("support_pct", 0),
            "oppose_pct": s.get("oppose_pct", 0),
            "num_personas": s.get("num_personas", 0),
            "created_at": s.get("created_at", ""),
        })
    return out


def get_simulation(sim_id: str) -> dict | None:
    """Retrieve a specific simulation's full data."""
    store = _read_store()
    for s in store:
        if s["id"] == sim_id:
            return s
    return None
