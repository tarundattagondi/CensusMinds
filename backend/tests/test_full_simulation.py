"""
End-to-end test: Full simulation pipeline.
Fetches census data, generates personas, runs LLM simulation, and aggregates results.

Requires ANTHROPIC_API_KEY in .env (CENSUS_API_KEY optional — works without it).
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.services.census_service import fetch_demographics
from backend.services.persona_generator import generate_personas
from backend.services.llm_service import simulate_batch
from backend.services.aggregator import aggregate_results

POLICY = (
    "The city is proposing to remove 200 street parking spots downtown "
    "to add protected bike lanes on Main Street"
)


async def main():
    zip_code = "22030"
    num_personas = 5

    # Step 1: Fetch census data
    print(f"[1/4] Fetching census data for ZIP {zip_code}...")
    census_data = await fetch_demographics(zip_code)
    print(f"       Population: {census_data['total_population']:,}")
    print(f"       Median Income: ${census_data['median_household_income']:,}")

    # Step 2: Generate personas
    print(f"\n[2/4] Generating {num_personas} personas...")
    personas = generate_personas(census_data, n=num_personas)
    for p in personas:
        print(f"       #{p['id']} {p['name']} — {p['age']}yo {p['ethnicity']}, {p['job_title']}, {p['commute_mode']}")

    # Step 3: Run LLM simulation
    print(f"\n[3/4] Running LLM simulation...")
    print(f"       Policy: \"{POLICY}\"")
    responses = await simulate_batch(personas, POLICY, batch_size=5)

    print("\n       --- Individual Responses ---")
    for r in responses:
        print(f"       {r['persona_name']}: {r['stance']} | Impact: {r['impact_level']} | Attend: {r['would_attend']}")
        print(f"         Reasoning: {r['reasoning']}")
        print(f"         Suggestion: {r['suggested_modification']}")
        print()

    # Step 4: Aggregate results
    print("[4/4] Aggregating results...")
    results = aggregate_results(responses)

    print("\n" + "=" * 70)
    print("SIMULATION RESULTS")
    print("=" * 70)

    summary = results["summary"]
    print(f"\nOverall: {summary['support_pct']}% SUPPORT / {summary['oppose_pct']}% OPPOSE")
    print(f"({summary['support_count']} support, {summary['oppose_count']} oppose out of {summary['valid_responses']} valid)")

    print(f"\nImpact Distribution:")
    for level, pct in results["impact_distribution"].items():
        print(f"  {level}: {pct}%")

    print(f"\nAttendance: {results['attendance']['would_attend_pct']}% would attend a public meeting")

    print("\n--- Breakdown by Income ---")
    for group, data in results["breakdown_by_income"].items():
        print(f"  {group}: {data['support_pct']}% support / {data['oppose_pct']}% oppose (n={data['total']})")

    print("\n--- Breakdown by Age Group ---")
    for group, data in results["breakdown_by_age_group"].items():
        print(f"  {group}: {data['support_pct']}% support / {data['oppose_pct']}% oppose (n={data['total']})")

    print("\n--- Breakdown by Commute Mode ---")
    for group, data in results["breakdown_by_commute"].items():
        print(f"  {group}: {data['support_pct']}% support / {data['oppose_pct']}% oppose (n={data['total']})")

    print("\n--- Breakdown by Housing ---")
    for group, data in results["breakdown_by_housing"].items():
        print(f"  {group}: {data['support_pct']}% support / {data['oppose_pct']}% oppose (n={data['total']})")

    if results["hidden_impacts"]:
        print("\n--- Hidden Impacts (high impact, low attendance) ---")
        for h in results["hidden_impacts"]:
            print(f"  {h['group']}: {h['high_impact_count']} highly impacted, {h['would_not_attend_count']} wouldn't attend")
            print(f"    {h['risk']}")
    else:
        print("\n--- No hidden impacts detected ---")

    if results["top_concerns"]:
        print("\n--- Top Concerns (from opponents) ---")
        for i, c in enumerate(results["top_concerns"], 1):
            print(f"  {i}. {c}")

    if results["top_benefits"]:
        print("\n--- Top Benefits (from supporters) ---")
        for i, b in enumerate(results["top_benefits"], 1):
            print(f"  {i}. {b}")

    if results["suggested_modifications"]:
        print("\n--- Suggested Modifications ---")
        for m in results["suggested_modifications"]:
            print(f"  {m['persona']}: {m['suggestion']}")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
