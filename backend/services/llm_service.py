"""LLM simulation service — runs each persona through Claude to evaluate a policy."""

import os
import asyncio
import json
import re
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

DEFAULT_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-20250514"


def _get_client(api_key: str | None = None) -> AsyncAnthropic:
    """Get an Anthropic client, using the provided key or the default."""
    return AsyncAnthropic(api_key=api_key or DEFAULT_API_KEY)


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
        f"- Personality Traits: {traits}\n\n"
        f"IMPORTANT: You must respond ONLY with a valid JSON object. "
        f"No markdown, no code blocks, no explanation before or after. Just the raw JSON."
    )


def _build_user_prompt(policy: str) -> str:
    """Build the user prompt asking the persona to evaluate a policy."""
    return (
        f"A new local policy has been proposed:\n\n"
        f"\"{policy}\"\n\n"
        f"Respond ONLY with a valid JSON object. No markdown, no code blocks, no explanation before or after. "
        f"Just the raw JSON object in this exact format:\n\n"
        f"{{\"stance\": \"SUPPORT\", \"impact_level\": \"MEDIUM\", "
        f"\"reasoning\": \"2-3 sentences here\", \"would_attend\": \"YES\", "
        f"\"suggested_modification\": \"one suggestion here\"}}\n\n"
        f"Rules:\n"
        f"- stance must be exactly \"SUPPORT\" or \"OPPOSE\"\n"
        f"- impact_level must be exactly \"NONE\", \"LOW\", \"MEDIUM\", \"HIGH\", or \"CRITICAL\"\n"
        f"- would_attend must be exactly \"YES\" or \"NO\"\n"
        f"- reasoning should be 2-3 sentences about how this affects YOUR life"
    )


def _persona_base(persona: dict) -> dict:
    """Return the base persona fields shared by all response types."""
    return {
        "persona_id": persona["id"],
        "persona_name": persona["name"],
        "age": persona["age"],
        "income_range": persona["income_range"],
        "housing_type": persona["housing_type"],
        "commute_mode": persona["commute_mode"],
        "education": persona["education"],
        "ethnicity": persona["ethnicity"],
    }


def _extract_field(text: str, field: str, options: list[str] | None = None) -> str:
    """Try to extract a field value from raw text using keyword matching."""
    if options:
        text_upper = text.upper()
        for opt in options:
            if opt.upper() in text_upper:
                return opt.upper()
    pattern = rf'"{field}"\s*:\s*"([^"]*)"'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def _parse_response(text: str, persona: dict) -> dict:
    """Parse the LLM response into a structured dictionary with multiple fallbacks."""
    base = _persona_base(persona)

    # Strip markdown code blocks if present
    cleaned = text.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()

    # Try 1: Parse the cleaned text directly as JSON
    try:
        data = json.loads(cleaned)
        return {
            **base,
            "stance": str(data.get("stance", "UNKNOWN")).upper(),
            "impact_level": str(data.get("impact_level", "UNKNOWN")).upper(),
            "reasoning": str(data.get("reasoning", "")),
            "would_attend": str(data.get("would_attend", "NO")).upper(),
            "suggested_modification": str(data.get("suggested_modification", "")),
        }
    except (json.JSONDecodeError, ValueError):
        pass

    # Try 2: Find JSON object within the text using regex
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return {
                **base,
                "stance": str(data.get("stance", "UNKNOWN")).upper(),
                "impact_level": str(data.get("impact_level", "UNKNOWN")).upper(),
                "reasoning": str(data.get("reasoning", "")),
                "would_attend": str(data.get("would_attend", "NO")).upper(),
                "suggested_modification": str(data.get("suggested_modification", "")),
            }
        except (json.JSONDecodeError, ValueError):
            pass

    # Try 3: Fallback — extract fields from raw text using keyword matching
    print(f"[LLM PARSE WARNING] Failed to parse JSON for persona {persona['name']}. Raw response:\n{text[:500]}")

    stance = _extract_field(text, "stance", ["SUPPORT", "OPPOSE"])
    impact = _extract_field(text, "impact_level", ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
    attend = _extract_field(text, "would_attend", ["YES", "NO"])
    reasoning = _extract_field(text, "reasoning")
    modification = _extract_field(text, "suggested_modification")

    if not reasoning:
        # Use the first substantial sentence as reasoning
        sentences = [s.strip() for s in re.split(r'[.!]', text) if len(s.strip()) > 20]
        reasoning = ". ".join(sentences[:2]) + "." if sentences else text[:200]

    return {
        **base,
        "stance": stance or "UNKNOWN",
        "impact_level": impact or "UNKNOWN",
        "reasoning": reasoning,
        "would_attend": attend or "NO",
        "suggested_modification": modification or "",
    }


async def simulate_persona(persona: dict, policy: str, api_key: str | None = None) -> dict:
    """Run a single persona through the LLM simulation."""
    client = _get_client(api_key)
    response = await client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=_build_system_prompt(persona),
        messages=[{"role": "user", "content": _build_user_prompt(policy)}],
    )
    text = response.content[0].text
    return _parse_response(text, persona)


async def simulate_batch(personas: list[dict], policy: str, batch_size: int = 10, api_key: str | None = None) -> list[dict]:
    """
    Run all personas through the LLM simulation in parallel batches.
    Processes batch_size personas concurrently to respect rate limits.
    """
    results = []
    for i in range(0, len(personas), batch_size):
        batch = personas[i : i + batch_size]
        batch_results = await asyncio.gather(
            *[simulate_persona(p, policy, api_key=api_key) for p in batch],
            return_exceptions=True,
        )
        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                persona = batch[j]
                print(f"[LLM ERROR] Persona {persona['name']}: {result}")
                results.append({
                    **_persona_base(persona),
                    "stance": "ERROR",
                    "impact_level": "UNKNOWN",
                    "reasoning": f"Simulation error: {str(result)[:200]}",
                    "would_attend": "NO",
                    "suggested_modification": "",
                })
            else:
                results.append(result)
    return results
