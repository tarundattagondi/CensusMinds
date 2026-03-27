"""
Test script: Fetch census data for ZIP 22030 (Fairfax, VA)
and generate 10 sample personas.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.services.census_service import fetch_demographics
from backend.services.persona_generator import generate_personas


async def main():
    zip_code = "22030"
    print(f"Fetching census data for ZIP {zip_code} (Fairfax, VA)...\n")

    census_data = await fetch_demographics(zip_code)

    print("=" * 60)
    print(f"CENSUS DATA FOR ZIP {zip_code}")
    print("=" * 60)
    print(f"Total Population: {census_data['total_population']:,}")
    print(f"Total Households: {census_data['total_households']:,}")
    print(f"Median Household Income: ${census_data['median_household_income']:,}")

    print("\n--- Age Distribution ---")
    for k, v in census_data["age_distribution"].items():
        print(f"  {k}: {v}%")

    print("\n--- Race/Ethnicity ---")
    for k, v in census_data["race_ethnicity"].items():
        print(f"  {k}: {v}%")

    print("\n--- Income Brackets ---")
    for k, v in census_data["income_brackets"].items():
        print(f"  {k}: {v}%")

    print("\n--- Education Levels ---")
    for k, v in census_data["education"].items():
        print(f"  {k}: {v}%")

    print("\n--- Commute Modes ---")
    for k, v in census_data["commute_mode"].items():
        print(f"  {k}: {v}%")

    print("\n--- Housing Tenure ---")
    for k, v in census_data["housing_tenure"].items():
        print(f"  {k}: {v}%")

    print("\n--- Vehicles per Household ---")
    for k, v in census_data["vehicles_per_household"].items():
        print(f"  {k}: {v}%")

    # Generate personas
    print("\n" + "=" * 60)
    print("GENERATED PERSONAS (10)")
    print("=" * 60)

    personas = generate_personas(census_data, n=10)
    for p in personas:
        print(f"\n--- Persona #{p['id']} ---")
        print(f"  Name:       {p['name']}")
        print(f"  Age:        {p['age']}")
        print(f"  Gender:     {p['gender']}")
        print(f"  Ethnicity:  {p['ethnicity']}")
        print(f"  Education:  {p['education']}")
        print(f"  Job:        {p['job_title']}")
        print(f"  Income:     {p['income_range']}")
        print(f"  Housing:    {p['housing_type']}")
        print(f"  Household:  {p['household_type']}")
        print(f"  Commute:    {p['commute_mode']}")
        print(f"  Vehicles:   {p['vehicles']}")
        print(f"  Traits:     {', '.join(p['personality_traits'])}")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
