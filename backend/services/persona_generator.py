import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with open(DATA_DIR / "names.json") as f:
    NAMES = json.load(f)

with open(DATA_DIR / "jobs.json") as f:
    JOBS = json.load(f)

# Maps census age brackets to (min_age, max_age) ranges
AGE_BRACKETS = {
    "under_5": (0, 4),
    "5_to_9": (5, 9),
    "10_to_14": (10, 14),
    "15_to_19": (15, 19),
    "20_to_24": (20, 24),
    "25_to_34": (25, 34),
    "35_to_44": (35, 44),
    "45_to_54": (45, 54),
    "55_to_59": (55, 59),
    "60_to_64": (60, 64),
    "65_to_74": (65, 74),
    "75_to_84": (75, 84),
    "85_plus": (85, 95),
}

INCOME_RANGES = {
    "under_10k": "Under $10,000",
    "10k_to_15k": "$10,000-$14,999",
    "15k_to_25k": "$15,000-$24,999",
    "25k_to_35k": "$25,000-$34,999",
    "35k_to_50k": "$35,000-$49,999",
    "50k_to_75k": "$50,000-$74,999",
    "75k_to_100k": "$75,000-$99,999",
    "100k_to_150k": "$100,000-$149,999",
    "150k_to_200k": "$150,000-$199,999",
    "200k_plus": "$200,000+",
}

COMMUTE_MODES = {
    "car_alone": "Drives alone",
    "carpool": "Carpool",
    "public_transit": "Public transit",
    "walked": "Walks",
    "other": "Other",
    "work_from_home": "Work from home",
}

EDUCATION_LEVELS = {
    "less_than_9th": "Less than 9th grade",
    "9th_to_12th_no_diploma": "Some high school",
    "high_school_graduate": "High school diploma",
    "some_college": "Some college",
    "associates_degree": "Associate's degree",
    "bachelors_degree": "Bachelor's degree",
    "graduate_degree": "Graduate degree",
}

ETHNICITY_MAP = {
    "white": "white",
    "black": "black",
    "asian": "asian",
    "hispanic": "hispanic",
    "native_american": "native_american",
    "pacific_islander": "pacific_islander",
    "two_or_more": "two_or_more",
}

HOUSING_TYPES = {
    "owner_occupied": "Homeowner",
    "renter_occupied": "Renter",
}

HOUSEHOLD_TYPES = {
    "married_couple": "Married couple",
    "male_householder_no_spouse": "Single male householder",
    "female_householder_no_spouse": "Single female householder",
    "nonfamily": "Living alone / with roommates",
}

PERSONALITY_TRAITS = [
    "community-oriented", "independent", "frugal", "entrepreneurial",
    "tech-savvy", "traditional", "environmentally conscious", "family-focused",
    "career-driven", "health-conscious", "politically active", "creative",
    "socially engaged", "introverted", "outdoorsy", "religious",
    "civic-minded", "pragmatic", "ambitious", "laid-back",
    "education-focused", "risk-averse", "optimistic", "skeptical",
]

# Map education keys to job JSON keys
EDUCATION_TO_JOB_KEY = {
    "less_than_9th": "less_than_high_school",
    "9th_to_12th_no_diploma": "less_than_high_school",
    "high_school_graduate": "high_school",
    "some_college": "some_college",
    "associates_degree": "associates",
    "bachelors_degree": "bachelors",
    "graduate_degree": "graduate",
}


def _weighted_choice(distribution: dict) -> str:
    """Pick a key from a {key: percentage} dict using weighted random sampling."""
    keys = list(distribution.keys())
    weights = [max(distribution[k], 0) for k in keys]
    total = sum(weights)
    if total == 0:
        return random.choice(keys)
    return random.choices(keys, weights=weights, k=1)[0]


def _pick_name(ethnicity_key: str, gender: str) -> tuple[str, str]:
    """Pick a first and last name based on ethnicity."""
    name_data = NAMES.get(ethnicity_key, NAMES["white"])
    if gender == "male":
        first = random.choice(name_data["first_male"])
    else:
        first = random.choice(name_data["first_female"])
    last = random.choice(name_data["last"])
    return first, last


def _pick_job(education_key: str, age: int) -> str:
    """Pick a job title based on education level."""
    if age < 16:
        return "Student"
    if age >= 67:
        return random.choice(["Retired", "Retired", "Retired", "Part-time worker", "Consultant"])

    job_key = EDUCATION_TO_JOB_KEY.get(education_key, "high_school")
    job_categories = JOBS.get(job_key, JOBS["high_school"])
    category = random.choice(list(job_categories.values()))
    return random.choice(category)


def generate_personas(census_data: dict, n: int = 100) -> list[dict]:
    """
    Generate N personas using weighted random sampling based on census demographics.
    Each persona statistically matches the ZIP code's real distributions.
    """
    personas = []

    for i in range(n):
        # Sample each attribute from census distributions
        age_bracket = _weighted_choice(census_data["age_distribution"])
        min_age, max_age = AGE_BRACKETS[age_bracket]
        age = random.randint(min_age, max_age)

        ethnicity_key = _weighted_choice(census_data["race_ethnicity"])
        ethnicity_label = ethnicity_key.replace("_", " ").title()

        gender = random.choice(["male", "female"])
        first_name, last_name = _pick_name(
            ETHNICITY_MAP.get(ethnicity_key, "white"), gender
        )

        education_key = _weighted_choice(census_data["education"])
        # Adjust education for young people
        if age < 18:
            education_key = "less_than_9th"
        elif age < 22:
            education_key = random.choice(["high_school_graduate", "some_college", "9th_to_12th_no_diploma"])

        income_key = _weighted_choice(census_data["income_brackets"])
        housing_key = _weighted_choice(census_data["housing_tenure"])
        commute_key = _weighted_choice(census_data["commute_mode"])
        vehicle_key = _weighted_choice(census_data["vehicles_per_household"])
        household_key = _weighted_choice(census_data["household_type"])

        job_title = _pick_job(education_key, age)
        traits = random.sample(PERSONALITY_TRAITS, k=random.randint(2, 3))

        vehicles_map = {
            "no_vehicle": 0,
            "one_vehicle": 1,
            "two_vehicles": 2,
            "three_plus": random.randint(3, 4),
        }

        persona = {
            "id": i + 1,
            "name": f"{first_name} {last_name}",
            "age": age,
            "gender": gender,
            "ethnicity": ethnicity_label,
            "income_range": INCOME_RANGES.get(income_key, "Unknown"),
            "housing_type": HOUSING_TYPES.get(housing_key, "Unknown"),
            "commute_mode": COMMUTE_MODES.get(commute_key, "Unknown"),
            "education": EDUCATION_LEVELS.get(education_key, "Unknown"),
            "job_title": job_title,
            "household_type": HOUSEHOLD_TYPES.get(household_key, "Unknown"),
            "vehicles": vehicles_map.get(vehicle_key, 1),
            "personality_traits": traits,
        }
        personas.append(persona)

    return personas
