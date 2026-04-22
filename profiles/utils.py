import pycountry

def get_age_group(age):
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    return "senior"


def get_top_country(countries):
    if not countries:
        return None, None
    top = max(countries, key=lambda x: x.get("probability", 0))
    return top.get("country_id"), top.get("probability")


def get_country_name(country_id):
    try:
        country = pycountry.countries.get(alpha_2=country_id)
        return country.name if country else "Unknown"
    except:
        return "Unknown"