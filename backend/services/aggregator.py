import re
from collections import Counter


def _pct(count: int, total: int) -> float:
    """Calculate percentage, rounded to 1 decimal."""
    if total == 0:
        return 0.0
    return round((count / total) * 100, 1)


def _breakdown_by_field(responses: list[dict], field: str) -> dict:
    """Compute support/oppose breakdown grouped by a persona field."""
    groups = {}
    for r in responses:
        key = r.get(field, "Unknown")
        if key not in groups:
            groups[key] = {"support": 0, "oppose": 0, "total": 0}
        groups[key]["total"] += 1
        if r["stance"] == "SUPPORT":
            groups[key]["support"] += 1
        elif r["stance"] == "OPPOSE":
            groups[key]["oppose"] += 1

    result = {}
    for key, counts in groups.items():
        result[key] = {
            "support_pct": _pct(counts["support"], counts["total"]),
            "oppose_pct": _pct(counts["oppose"], counts["total"]),
            "total": counts["total"],
        }
    return result


def _age_group(age: int) -> str:
    """Bin an age into a readable group."""
    if age < 18:
        return "Under 18"
    elif age < 25:
        return "18-24"
    elif age < 35:
        return "25-34"
    elif age < 45:
        return "35-44"
    elif age < 55:
        return "45-54"
    elif age < 65:
        return "55-64"
    else:
        return "65+"


def _extract_top_themes(responses: list[dict], stance_filter: str, top_n: int = 5) -> list[str]:
    """
    Extract the most common themes from reasoning text for a given stance.
    Uses simple keyword frequency on sentence fragments.
    """
    sentences = []
    for r in responses:
        if r["stance"] != stance_filter:
            continue
        reasoning = r.get("reasoning", "")
        # Split reasoning into sentences
        for s in re.split(r'[.!]', reasoning):
            s = s.strip()
            if len(s) > 15:
                sentences.append(s)

    if not sentences:
        return []

    # Extract key phrases by finding common noun-phrase-like patterns
    # Simple approach: count 2-3 word phrases
    phrase_counter = Counter()
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "each",
        "every", "both", "few", "more", "most", "other", "some", "such", "no",
        "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "just", "because", "but", "and", "or", "if", "while", "that", "this",
        "these", "those", "it", "its", "i", "my", "me", "we", "our", "you",
        "your", "he", "his", "she", "her", "they", "their", "them", "what",
        "which", "who", "whom", "whose", "would", "also", "about", "up",
    }

    for sentence in sentences:
        words = re.findall(r'[a-z]+', sentence.lower())
        words = [w for w in words if w not in stop_words and len(w) > 2]
        # Count bigrams and trigrams
        for size in (2, 3):
            for i in range(len(words) - size + 1):
                phrase = " ".join(words[i:i + size])
                phrase_counter[phrase] += 1

    # Return the most common phrases, deduplicated
    top_phrases = []
    seen_words = set()
    for phrase, count in phrase_counter.most_common(top_n * 3):
        if count < 2:
            continue
        phrase_words = set(phrase.split())
        # Skip if too similar to an already-selected phrase
        if phrase_words & seen_words == phrase_words:
            continue
        top_phrases.append(phrase)
        seen_words.update(phrase_words)
        if len(top_phrases) >= top_n:
            break

    # If not enough recurring phrases, fall back to full sentences
    if len(top_phrases) < top_n:
        for sentence in sentences[:top_n - len(top_phrases)]:
            if sentence not in top_phrases:
                top_phrases.append(sentence)

    return top_phrases[:top_n]


def _find_hidden_impacts(responses: list[dict]) -> list[dict]:
    """
    Identify demographic groups where impact is HIGH/CRITICAL
    but most members would NOT attend a public meeting.
    These are the voices least likely to be heard.
    """
    # Group by demographic fields
    group_fields = ["income_range", "ethnicity", "housing_type", "commute_mode", "education"]
    hidden = []

    for field in group_fields:
        groups = {}
        for r in responses:
            key = r.get(field, "Unknown")
            if key not in groups:
                groups[key] = {"high_impact": 0, "would_not_attend": 0, "total": 0, "personas": []}
            groups[key]["total"] += 1
            if r["impact_level"] in ("HIGH", "CRITICAL"):
                groups[key]["high_impact"] += 1
                if r["would_attend"] == "NO":
                    groups[key]["would_not_attend"] += 1
                    groups[key]["personas"].append(r["persona_name"])

        for key, data in groups.items():
            if data["high_impact"] >= 2 and data["would_not_attend"] > data["high_impact"] * 0.5:
                hidden.append({
                    "group": f"{field}: {key}",
                    "high_impact_count": data["high_impact"],
                    "would_not_attend_count": data["would_not_attend"],
                    "total_in_group": data["total"],
                    "example_personas": data["personas"][:3],
                    "risk": "These residents are significantly impacted but unlikely to voice concerns at public meetings.",
                })

    return hidden


def aggregate_results(responses: list[dict]) -> dict:
    """
    Aggregate all persona simulation responses into a complete results dictionary.
    """
    total = len(responses)
    valid = [r for r in responses if r["stance"] in ("SUPPORT", "OPPOSE")]
    valid_total = len(valid)

    support_count = sum(1 for r in valid if r["stance"] == "SUPPORT")
    oppose_count = sum(1 for r in valid if r["stance"] == "OPPOSE")

    # Impact level distribution
    impact_counts = Counter(r["impact_level"] for r in responses)
    attendance_yes = sum(1 for r in responses if r["would_attend"] == "YES")

    # Add age_group to each response for grouping
    responses_with_age_group = []
    for r in responses:
        r_copy = dict(r)
        r_copy["age_group"] = _age_group(r["age"])
        responses_with_age_group.append(r_copy)

    return {
        "summary": {
            "total_personas": total,
            "valid_responses": valid_total,
            "support_pct": _pct(support_count, valid_total),
            "oppose_pct": _pct(oppose_count, valid_total),
            "support_count": support_count,
            "oppose_count": oppose_count,
        },
        "impact_distribution": {
            level: _pct(count, total)
            for level, count in impact_counts.most_common()
        },
        "attendance": {
            "would_attend_pct": _pct(attendance_yes, total),
            "would_not_attend_pct": _pct(total - attendance_yes, total),
        },
        "breakdown_by_income": _breakdown_by_field(responses, "income_range"),
        "breakdown_by_age_group": _breakdown_by_field(responses_with_age_group, "age_group"),
        "breakdown_by_commute": _breakdown_by_field(responses, "commute_mode"),
        "breakdown_by_housing": _breakdown_by_field(responses, "housing_type"),
        "breakdown_by_education": _breakdown_by_field(responses, "education"),
        "breakdown_by_ethnicity": _breakdown_by_field(responses, "ethnicity"),
        "top_concerns": _extract_top_themes(responses, "OPPOSE", top_n=5),
        "top_benefits": _extract_top_themes(responses, "SUPPORT", top_n=5),
        "hidden_impacts": _find_hidden_impacts(responses),
        "suggested_modifications": [
            {"persona": r["persona_name"], "suggestion": r["suggested_modification"]}
            for r in responses
            if r.get("suggested_modification")
        ],
        "all_responses": responses,
    }
