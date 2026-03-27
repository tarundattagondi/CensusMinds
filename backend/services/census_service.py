"""Census data service — fetches real demographics from the US Census ACS 5-Year API."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
BASE_URL = "https://api.census.gov/data/2022/acs/acs5/profile"


async def _fetch_table(zcta: str, table: str, fields: list[str]) -> dict:
    """Fetch specific fields from a Census ACS 5-Year profile table for a ZCTA."""
    params = {
        "get": ",".join(fields),
        "for": f"zip code tabulation area:{zcta}",
    }
    if CENSUS_API_KEY and CENSUS_API_KEY.strip():
        params["key"] = CENSUS_API_KEY.strip()
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "json" not in content_type and "text/html" in content_type:
            raise ValueError(f"Census API returned HTML instead of JSON (likely invalid API key). URL: {resp.url}")
        data = resp.json()

    headers = data[0]
    values = data[1]
    return dict(zip(headers, values))


def _pct(raw: dict, key: str) -> float:
    """Safely parse a percentage value from census data."""
    val = raw.get(key)
    if val is None or val == "-" or val == "(X)" or val == "N":
        return 0.0
    return float(val)


def _count(raw: dict, key: str) -> int:
    """Safely parse a count value from census data."""
    val = raw.get(key)
    if val is None or val == "-" or val == "(X)" or val == "N":
        return 0
    return int(float(val))


async def fetch_demographics(zip_code: str) -> dict:
    """
    Fetch real demographic data from US Census ACS 5-Year API for a ZIP code.
    Returns a clean dictionary with percentage distributions for each category.
    """
    zcta = zip_code.strip()

    # DP05 - Demographic characteristics (age, sex, race/ethnicity)
    dp05_fields = [
        "DP05_0001E",  # Total population
        # Age distribution (percent)
        "DP05_0005PE",  # Under 5
        "DP05_0006PE",  # 5-9
        "DP05_0007PE",  # 10-14
        "DP05_0008PE",  # 15-19
        "DP05_0009PE",  # 20-24
        "DP05_0010PE",  # 25-34
        "DP05_0011PE",  # 35-44
        "DP05_0012PE",  # 45-54
        "DP05_0013PE",  # 55-59
        "DP05_0014PE",  # 60-64
        "DP05_0015PE",  # 65-74
        "DP05_0016PE",  # 75-84
        "DP05_0017PE",  # 85+
        # Race/ethnicity (percent)
        "DP05_0037PE",  # White alone
        "DP05_0038PE",  # Black or African American alone
        "DP05_0044PE",  # Asian alone
        "DP05_0071PE",  # Hispanic or Latino
        "DP05_0039PE",  # American Indian/Alaska Native alone
        "DP05_0052PE",  # Native Hawaiian/Pacific Islander alone
        "DP05_0057PE",  # Two or more races
    ]

    # DP03 - Economic characteristics (income, employment, commute)
    dp03_fields = [
        # Income brackets (percent of households)
        "DP03_0052PE",  # Less than $10,000
        "DP03_0053PE",  # $10,000-$14,999
        "DP03_0054PE",  # $15,000-$24,999
        "DP03_0055PE",  # $25,000-$34,999
        "DP03_0056PE",  # $35,000-$49,999
        "DP03_0057PE",  # $50,000-$74,999
        "DP03_0058PE",  # $75,000-$99,999
        "DP03_0059PE",  # $100,000-$149,999
        "DP03_0060PE",  # $150,000-$199,999
        "DP03_0061PE",  # $200,000+
        "DP03_0062E",   # Median household income
        # Commute mode (percent)
        "DP03_0019PE",  # Car alone
        "DP03_0020PE",  # Carpool
        "DP03_0021PE",  # Public transit
        "DP03_0022PE",  # Walked
        "DP03_0023PE",  # Other means
        "DP03_0024PE",  # Work from home
    ]

    # DP02 - Social characteristics (education, household type)
    dp02_fields = [
        # Education (percent of 25+)
        "DP02_0060PE",  # Less than 9th grade
        "DP02_0061PE",  # 9th-12th, no diploma
        "DP02_0062PE",  # High school graduate
        "DP02_0063PE",  # Some college, no degree
        "DP02_0064PE",  # Associate's degree
        "DP02_0065PE",  # Bachelor's degree
        "DP02_0066PE",  # Graduate/professional degree
        # Household type (percent)
        "DP02_0001E",   # Total households
        "DP02_0003PE",  # Married-couple family
        "DP02_0007PE",  # Male householder, no spouse
        "DP02_0011PE",  # Female householder, no spouse
        "DP02_0012PE",  # Nonfamily households
    ]

    # DP04 - Housing characteristics (tenure, vehicles)
    dp04_fields = [
        # Tenure (percent)
        "DP04_0046PE",  # Owner-occupied
        "DP04_0047PE",  # Renter-occupied
        # Vehicles available (percent of occupied units)
        "DP04_0058PE",  # No vehicles
        "DP04_0059PE",  # 1 vehicle
        "DP04_0060PE",  # 2 vehicles
        "DP04_0061PE",  # 3+ vehicles
    ]

    # Fetch all tables concurrently
    dp05, dp03, dp02, dp04 = await _fetch_all_tables(zcta, dp05_fields, dp03_fields, dp02_fields, dp04_fields)

    return {
        "zip_code": zip_code,
        "total_population": _count(dp05, "DP05_0001E"),
        "total_households": _count(dp02, "DP02_0001E"),
        "median_household_income": _count(dp03, "DP03_0062E"),
        "age_distribution": {
            "under_5": _pct(dp05, "DP05_0005PE"),
            "5_to_9": _pct(dp05, "DP05_0006PE"),
            "10_to_14": _pct(dp05, "DP05_0007PE"),
            "15_to_19": _pct(dp05, "DP05_0008PE"),
            "20_to_24": _pct(dp05, "DP05_0009PE"),
            "25_to_34": _pct(dp05, "DP05_0010PE"),
            "35_to_44": _pct(dp05, "DP05_0011PE"),
            "45_to_54": _pct(dp05, "DP05_0012PE"),
            "55_to_59": _pct(dp05, "DP05_0013PE"),
            "60_to_64": _pct(dp05, "DP05_0014PE"),
            "65_to_74": _pct(dp05, "DP05_0015PE"),
            "75_to_84": _pct(dp05, "DP05_0016PE"),
            "85_plus": _pct(dp05, "DP05_0017PE"),
        },
        "race_ethnicity": {
            "white": _pct(dp05, "DP05_0037PE"),
            "black": _pct(dp05, "DP05_0038PE"),
            "asian": _pct(dp05, "DP05_0044PE"),
            "hispanic": _pct(dp05, "DP05_0071PE"),
            "native_american": _pct(dp05, "DP05_0039PE"),
            "pacific_islander": _pct(dp05, "DP05_0052PE"),
            "two_or_more": _pct(dp05, "DP05_0057PE"),
        },
        "income_brackets": {
            "under_10k": _pct(dp03, "DP03_0052PE"),
            "10k_to_15k": _pct(dp03, "DP03_0053PE"),
            "15k_to_25k": _pct(dp03, "DP03_0054PE"),
            "25k_to_35k": _pct(dp03, "DP03_0055PE"),
            "35k_to_50k": _pct(dp03, "DP03_0056PE"),
            "50k_to_75k": _pct(dp03, "DP03_0057PE"),
            "75k_to_100k": _pct(dp03, "DP03_0058PE"),
            "100k_to_150k": _pct(dp03, "DP03_0059PE"),
            "150k_to_200k": _pct(dp03, "DP03_0060PE"),
            "200k_plus": _pct(dp03, "DP03_0061PE"),
        },
        "commute_mode": {
            "car_alone": _pct(dp03, "DP03_0019PE"),
            "carpool": _pct(dp03, "DP03_0020PE"),
            "public_transit": _pct(dp03, "DP03_0021PE"),
            "walked": _pct(dp03, "DP03_0022PE"),
            "other": _pct(dp03, "DP03_0023PE"),
            "work_from_home": _pct(dp03, "DP03_0024PE"),
        },
        "education": {
            "less_than_9th": _pct(dp02, "DP02_0060PE"),
            "9th_to_12th_no_diploma": _pct(dp02, "DP02_0061PE"),
            "high_school_graduate": _pct(dp02, "DP02_0062PE"),
            "some_college": _pct(dp02, "DP02_0063PE"),
            "associates_degree": _pct(dp02, "DP02_0064PE"),
            "bachelors_degree": _pct(dp02, "DP02_0065PE"),
            "graduate_degree": _pct(dp02, "DP02_0066PE"),
        },
        "housing_tenure": {
            "owner_occupied": _pct(dp04, "DP04_0046PE"),
            "renter_occupied": _pct(dp04, "DP04_0047PE"),
        },
        "vehicles_per_household": {
            "no_vehicle": _pct(dp04, "DP04_0058PE"),
            "one_vehicle": _pct(dp04, "DP04_0059PE"),
            "two_vehicles": _pct(dp04, "DP04_0060PE"),
            "three_plus": _pct(dp04, "DP04_0061PE"),
        },
        "household_type": {
            "married_couple": _pct(dp02, "DP02_0003PE"),
            "male_householder_no_spouse": _pct(dp02, "DP02_0007PE"),
            "female_householder_no_spouse": _pct(dp02, "DP02_0011PE"),
            "nonfamily": _pct(dp02, "DP02_0012PE"),
        },
    }


async def _fetch_all_tables(zcta, dp05_fields, dp03_fields, dp02_fields, dp04_fields):
    """Fetch all four census profile tables concurrently."""
    import asyncio

    results = await asyncio.gather(
        _fetch_table(zcta, "DP05", dp05_fields),
        _fetch_table(zcta, "DP03", dp03_fields),
        _fetch_table(zcta, "DP02", dp02_fields),
        _fetch_table(zcta, "DP04", dp04_fields),
    )
    return results
