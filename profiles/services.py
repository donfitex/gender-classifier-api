import requests
import pycountry


def get_gender(name):
    res = requests.get(f"https://api.genderize.io?name={name}", timeout=3)
    res.raise_for_status()
    return res.json()


def get_age(name):
    res = requests.get(f"https://api.agify.io?name={name}", timeout=3)
    res.raise_for_status()
    return res.json()


def get_country(name):
    res = requests.get(f"https://api.nationalize.io?name={name}", timeout=3)
    res.raise_for_status()
    return res.json()


def get_country_name(country_id):
    try:
        country = pycountry.countries.get(alpha_2=country_id)
        return country.name if country else "Unknown"
    except:
        return "Unknown"