import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer, ProfileListSerializer
from .services import get_gender, get_age, get_country, get_country_name


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


# =========================
# LIST + CREATE
# =========================
@api_view(['GET', 'POST'])
def profiles(request):

    # -------- GET --------
    if request.method == 'GET':
        qs = Profile.objects.all()

        gender = request.GET.get("gender")
        country_id = request.GET.get("country_id")
        age_group = request.GET.get("age_group")

        if gender:
            qs = qs.filter(gender__iexact=gender)

        if country_id:
            qs = qs.filter(country_id__iexact=country_id)

        if age_group:
            qs = qs.filter(age_group__iexact=age_group)

        serializer = ProfileListSerializer(qs, many=True)

        return Response({
            "status": "success",
            "count": qs.count(),
            "data": serializer.data
        })


    # -------- POST --------
    elif request.method == 'POST':
        name = request.data.get("name")

        if name is None:
            return Response(
                {"status": "error", "message": "Name is required"},
                status=400
            )

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

        # Idempotency
        existing = Profile.objects.filter(name=name).first()
        if existing:
            serializer = ProfileSerializer(existing)
            return Response(
                {
                    "status": "success",
                    "message": "Profile already exists",
                    "data": serializer.data
                },
                status=200
            )

        try:
            gender_data = get_gender(name)
            age_data = get_age(name)
            nation_data = get_country(name)

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
            country_name = get_country_name(country_id)

            profile = Profile.objects.create(
                name=name,
                gender=gender,
                gender_probability=probability,
                sample_size=count,
                age=age,
                age_group=age_group,
                country_name=country_name,
                country_id=country_id,
                country_probability=country_probability

            )

            serializer = ProfileSerializer(profile)

            return Response(
                {"status": "success", "data": serializer.data},
                status=201
            )

        except requests.exceptions.RequestException:
            return Response(
                {"status": "error", "message": "External API error"},
                status=502
            )


# =========================
# DETAIL (GET + DELETE)
# =========================
@api_view(['GET', 'DELETE'])
def profile_detail(request, id):
    try:
        profile = Profile.objects.get(id=id)

        if request.method == 'GET':
            serializer = ProfileSerializer(profile)
            return Response({
                "status": "success",
                "data": serializer.data
            })

        elif request.method == 'DELETE':
            profile.delete()
            return Response(status=204)

    except Profile.DoesNotExist:
        return Response(
            {"status": "error", "message": "Profile not found"},
            status=404
        )