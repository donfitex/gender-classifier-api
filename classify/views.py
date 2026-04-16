import requests
import logging
from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Profile

logger = logging.getLogger(__name__)


# =========================
# HELPERS
# =========================

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


def serialize_profile(profile):
    return {
        "id": str(profile.id),
        "name": profile.name,
        "gender": profile.gender,
        "gender_probability": profile.gender_probability,
        "sample_size": profile.sample_size,
        "age": profile.age,
        "age_group": profile.age_group,
        "country_id": profile.country_id,
        "country_probability": profile.country_probability,
        "created_at": profile.created_at.isoformat().replace("+00:00", "Z"),
    }


def fetch_json(url, api_name):
    try:
        res = requests.get(url, timeout=3)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return Response(
            {"status": "error", "message": f"{api_name} returned an invalid response"},
            status=502
        )


# =========================
# PROFILES (GET + POST)
# =========================

@api_view(['GET', 'POST'])
def profiles(request):

    # =========================
    # GET → LIST
    # =========================
    if request.method == 'GET':
        queryset = Profile.objects.all()

        gender = request.GET.get('gender')
        country_id = request.GET.get('country_id')
        age_group = request.GET.get('age_group')

        if gender:
            queryset = queryset.filter(gender__iexact=gender)

        if country_id:
            queryset = queryset.filter(country_id__iexact=country_id)

        if age_group:
            queryset = queryset.filter(age_group__iexact=age_group)

        data = [
            {
                "id": str(p.id),
                "name": p.name,
                "gender": p.gender,
                "age": p.age,
                "age_group": p.age_group,
                "country_id": p.country_id,
            }
            for p in queryset
        ]

        return Response({
            "status": "success",
            "count": len(data),
            "data": data
        })

    # =========================
    # POST → CREATE
    # =========================
    if request.method == 'POST':

        # STRICT VALIDATION
        if "name" not in request.data:
            return Response(
                {"status": "error", "message": "Name is required"},
                status=400
            )

        name = request.data.get("name")

        if not isinstance(name, str):
            return Response(
                {"status": "error", "message": "Name must be a string"},
                status=422
            )

        if name.strip() == "":
            return Response(
                {"status": "error", "message": "Name is required"},
                status=400
            )

        name = name.strip().lower()

        # IDEMPOTENCY
        existing = Profile.objects.filter(name=name).first()
        if existing:
            return Response(
                {
                    "status": "success",
                    "message": "Profile already exists",
                    "data": serialize_profile(existing)
                },
                status=200
            )

        # FETCH APIs
        gender_data = fetch_json(f"https://api.genderize.io?name={name}", "Genderize")
        if isinstance(gender_data, Response):
            return gender_data

        age_data = fetch_json(f"https://api.agify.io?name={name}", "Agify")
        if isinstance(age_data, Response):
            return age_data

        nation_data = fetch_json(f"https://api.nationalize.io?name={name}", "Nationalize")
        if isinstance(nation_data, Response):
            return nation_data

        # VALIDATE DATA

        # Gender
        gender = gender_data.get("gender")
        probability = gender_data.get("probability")
        count = gender_data.get("count")

        if gender is None or count == 0:
            return Response(
                {"status": "error", "message": "Genderize returned an invalid response"},
                status=502
            )

        # Age
        age = age_data.get("age")
        if age is None:
            return Response(
                {"status": "error", "message": "Agify returned an invalid response"},
                status=502
            )

        age_group = get_age_group(age)

        # Country
        country_id, country_probability = get_top_country(nation_data.get("country", []))

        if not country_id:
            return Response(
                {"status": "error", "message": "Nationalize returned an invalid response"},
                status=502
            )

        # SAVE
        profile = Profile.objects.create(
            name=name,
            gender=gender,
            gender_probability=probability,
            sample_size=count,
            age=age,
            age_group=age_group,
            country_id=country_id,
            country_probability=country_probability
        )

        return Response(
            {
                "status": "success",
                "data": serialize_profile(profile)
            },
            status=201
        )


# =========================
# DETAIL (GET + DELETE)
# =========================

@api_view(['GET', 'DELETE'])
def profile_detail(request, id):
    try:
        profile = Profile.objects.get(id=id)

        if request.method == 'GET':
            return Response({
                "status": "success",
                "data": serialize_profile(profile)
            })

        if request.method == 'DELETE':
            profile.delete()
            return Response(status=204)

    except Profile.DoesNotExist:
        return Response(
            {"status": "error", "message": "Profile not found"},
            status=404
        )
