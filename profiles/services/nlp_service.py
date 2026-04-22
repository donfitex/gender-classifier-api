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

    filters = {}

    # -------------------------
    # GENDER
    # -------------------------
    if "male" in q:
        filters["gender"] = "male"
    elif "female" in q:
        filters["gender"] = "female"

    # -------------------------
    # AGE GROUP (stored)
    # -------------------------
    for key, value in AGE_GROUPS.items():
        if key in q:
            filters["age_group"] = value
            break

    # -------------------------
    # SPECIAL: "young"
    # -------------------------
    if "young" in q:
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
    for country_name, code in COUNTRY_MAP.items():
        if country_name in q:
            filters["country_id"] = code
            break

    # -------------------------
    # VALIDATION (VERY IMPORTANT)
    # -------------------------
    if not filters:
        raise ValueError("Unable to interpret query")

    return filters