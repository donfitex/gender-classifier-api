COUNTRY_MAP = {
    "nigeria": "NG",
    "kenya": "KE",
    "angola": "AO",
}

def parse_query(q):
    q = q.lower()

    filters = {}

    if "male" in q:
        filters["gender"] = "male"
    elif "female" in q:
        filters["gender"] = "female"

    if "young" in q:
        filters["min_age"] = 16
        filters["max_age"] = 24

    if "above" in q:
        age = int(q.split("above")[1].strip().split()[0])
        filters["min_age"] = age

    for name, code in COUNTRY_MAP.items():
        if name in q:
            filters["country_id"] = code

    if not filters:
        return None

    return filters