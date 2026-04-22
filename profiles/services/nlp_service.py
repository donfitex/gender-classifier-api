import re

# -------------------------
# COUNTRY MAP (simple + safe)
# -------------------------
COUNTRY_MAP = {
    "nigeria": "NG",
    "kenya": "KE",
    "angola": "AO",
    "ghana": "GH",
    "benin": "BJ",
    "togo": "TG",
    "cameroon": "CM",
    "south africa": "ZA",
}

# -------------------------
# AGE GROUP KEYWORDS
# -------------------------
AGE_GROUPS = {
    "child": "child",
    "children": "child",
    "teen": "teenager",
    "teenager": "teenager",
    "teenagers": "teenager",
    "adult": "adult",
    "adults": "adult",
    "senior": "senior",
    "seniors": "senior",
}

# -------------------------
# MAIN PARSER
# -------------------------
def parse_query(query: str):
    if not query or not isinstance(query, str):
        raise ValueError("Invalid query parameters")

    q = query.lower().strip()

    words = re.findall(r"\b\w+\b", q.lower())

    filters = {}

    
    # -------------------------
    # GENDER
    # -------------------------
    has_male = "male" in words or "males" in words
    has_female = "female" in words or "females" in words

    if has_male and has_female:
        pass  # no filter (means both)
    elif has_female:
        filters["gender"] = "female"
    elif has_male:
        filters["gender"] = "male"

    # -------------------------
    # AGE GROUP (stored)
    # -------------------------
    if "child" in words or "children" in words:
        filters["age_group"] = "child"
    elif "teenager" in words or "teenagers" in words:
        filters["age_group"] = "teenager"
    elif "adult" in words or "adults" in words:
        filters["age_group"] = "adult"
    elif "senior" in words or "seniors" in words:
        filters["age_group"] = "senior"

    # -------------------------
    # SPECIAL: "young"
    # -------------------------
    if "young" in words:
        filters["min_age"] = 16
        filters["max_age"] = 24

    # -------------------------
    # AGE CONDITIONS
    # -------------------------
    above_match = re.search(r"(above|over)\s+(\d+)", q)
    if above_match:
        filters["min_age"] = int(above_match.group(2))

    below_match = re.search(r"(below|under)\s+(\d+)", q)
    if below_match:
        filters["max_age"] = int(below_match.group(2))

    between_match = re.search(r"between\s+(\d+)\s+and\s+(\d+)", q)
    if between_match:
        filters["min_age"] = int(between_match.group(1))
        filters["max_age"] = int(between_match.group(2))

    # -------------------------
    # COUNTRY
    # -------------------------
    for word in words:
        if word in COUNTRY_MAP:
            filters["country_id"] = COUNTRY_MAP[word]
            break

    # -------------------------
    # VALIDATION (VERY IMPORTANT)
    # -------------------------
    if not filters:
        return None

    return filters