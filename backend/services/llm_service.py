import os
import asyncio
import json
import re
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-20250514"


def _build_system_prompt(persona: dict) -> str:
    """Build a system prompt embedding the persona's full demographic profile."""
    traits = ", ".join(persona.get("personality_traits", []))
    return (
        f"You are roleplaying as {persona['name']}, a real resident of this community. "
        f"Stay fully in character and respond based on how this policy would actually affect your life.\n\n"
        f"YOUR PROFILE:\n"
        f"- Age: {persona['age']}\n"
        f"- Gender: {persona['gender']}\n"
        f"- Ethnicity: {persona['ethnicity']}\n"
        f"- Education: {persona['education']}\n"
        f"- Job: {persona['job_title']}\n"
        f"- Household Income: {persona['income_range']}\n"
        f"- Housing: {persona['housing_type']}\n"
        f"- Household Type: {persona['household_type']}\n"
        f"- Commute: {persona['commute_mode']}\n"
        f"- Vehicles: {persona['vehicles']}\n"
        f"- Personality Traits: {traits}\n"
    )


def _build_user_prompt(policy: str) -> str:
    """Build the user prompt asking the persona to evaluate a policy."""
    return (
        f"A new local policy has been proposed:\n\n"
        f"\"{policy}\"\n\n"
        f"As the person described in your profile, respond with EXACTLY this JSON format and nothing else:\n\n"
        f"{{\n"
        f"  \"stance\": \"SUPPORT\" or \"OPPOSE\",\n"
        f"  \"impact_level\": \"NONE\" or \"LOW\" or \"MEDIUM\" or \"HIGH\" or \"CRITICAL\",\n"
        f"  \"reasoning\": \"2-3 sentences explaining how this policy affects your daily life, finances, or community\",\n"
        f"  \"would_attend\": \"YES\" or \"NO\" (would you attend a public meeting about this?),\n"
        f"  \"suggested_modification\": \"One specific change you would suggest to improve this policy\"\n"
        f"}}"
    )


def _parse_response(text: str, persona: dict) -> dict:
    """Parse the LLM response into a structured dictionary."""
    # Try to extract JSON from the response
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return {
                "persona_id": persona["id"],
                "persona_name": persona["name"],
                "age": persona["age"],
                "income_range": persona["income_range"],
                "housing_type": persona["housing_type"],
                "commute_mode": persona["commute_mode"],
                "education": persona["education"],
                "ethnicity": persona["ethnicity"],
                "stance": data.get("stance", "UNKNOWN").upper(),
                "impact_level": data.get("impact_level", "UNKNOWN").upper(),
                "reasoning": data.get("reasoning", ""),
                "would_attend": data.get("would_attend", "NO").upper(),
                "suggested_modification": data.get("suggested_modification", ""),
            }
        except json.JSONDecodeError:
            pass

    # Fallback if JSON parsing fails
    return {
        "persona_id": persona["id"],
        "persona_name": persona["name"],
        "age": persona["age"],
        "income_range": persona["income_range"],
        "housing_type": persona["housing_type"],
        "commute_mode": persona["commute_mode"],
        "education": persona["education"],
        "ethnicity": persona["ethnicity"],
        "stance": "UNKNOWN",
        "impact_level": "UNKNOWN",
        "reasoning": text[:500],
        "would_attend": "NO",
        "suggested_modification": "",
    }


async def simulate_persona(persona: dict, policy: str) -> dict:
    """Run a single persona through the LLM simulation."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=_build_system_prompt(persona),
        messages=[{"role": "user", "content": _build_user_prompt(policy)}],
    )
    text = response.content[0].text
    return _parse_response(text, persona)


async def simulate_batch(personas: list[dict], policy: str, batch_size: int = 10) -> list[dict]:
    """
    Run all personas through the LLM simulation in parallel batches.
    Processes batch_size personas concurrently to respect rate limits.
    """
    results = []
    for i in range(0, len(personas), batch_size):
        batch = personas[i : i + batch_size]
        batch_results = await asyncio.gather(
            *[simulate_persona(p, policy) for p in batch],
            return_exceptions=True,
        )
        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                # Log the error and create a fallback response
                persona = batch[j]
                results.append({
                    "persona_id": persona["id"],
                    "persona_name": persona["name"],
                    "age": persona["age"],
                    "income_range": persona["income_range"],
                    "housing_type": persona["housing_type"],
                    "commute_mode": persona["commute_mode"],
                    "education": persona["education"],
                    "ethnicity": persona["ethnicity"],
                    "stance": "ERROR",
                    "impact_level": "UNKNOWN",
                    "reasoning": f"Error: {str(result)}",
                    "would_attend": "NO",
                    "suggested_modification": "",
                })
            else:
                results.append(result)
    return results
