from .external_service import fetch_gender, fetch_age, fetch_country
from ..models import Profile
from ..utils import get_age_group, get_country_name

def create_profile(name):
    name = name.strip().lower()

    existing = Profile.objects.filter(name=name).first()
    if existing:
        return existing, False

    gender_data = fetch_gender(name)
    age_data = fetch_age(name)
    country_data = fetch_country(name)

    if gender_data.get("gender") is None:
        raise Exception("Genderize")

    if age_data.get("age") is None:
        raise Exception("Agify")

    countries = country_data.get("country", [])
    if not countries:
        raise Exception("Nationalize")

    top = max(countries, key=lambda x: x["probability"])

    profile = Profile.objects.create(
        name=name,
        gender=gender_data["gender"],
        gender_probability=gender_data["probability"],
        age=age_data["age"],
        age_group=get_age_group(age_data["age"]),
        country_id=top["country_id"],
        country_name=get_country_name(top["country_id"]),
        country_probability=top["probability"]
    )

    return profile, True