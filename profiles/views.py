from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import ProfileSerializer, ProfileCreateSerializer
from .services.profile_service import create_profile
from .services.query_service import filter_profiles
from .services.nlp_service import parse_query


# =========================
# LIST + CREATE
# =========================
@api_view(['GET', 'POST'])
def profiles(request):

    # -------- GET --------
    if request.method == 'GET':
        try:
            result = filter_profiles(request.GET)

            serializer = ProfileSerializer(result["data"], many=True)

            return Response({
                "status": "success",
                "page": result["page"],
                "limit": result["limit"],
                "total": result["total"],
                "data": serializer.data
            })

        except ValueError:
            return Response(
                {"status": "error", "message": "Invalid query parameters"},
                status=400
            )


    # -------- POST --------
    elif request.method == 'POST':

        serializer = ProfileCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"status": "error", "message": serializer.errors},
                status=400
            )

        name = serializer.validated_data["name"]

        profile, created = create_profile(name)

        output = ProfileSerializer(profile)

        response = {
            "status": "success",
            "data": output.data
        }
        if not created:
            response["message"] = "Profile already exists"

        return Response(response, status=201 if created else 200)




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
                "data": ProfileSerializer(profile).data
            })

        elif request.method == 'DELETE':
            profile.delete()
            return Response(status=204)

    except Profile.DoesNotExist:
        return Response(
            {"status": "error", "message": "Profile not found"},
            status=404
        )


# =========================
# NLP SEARCH (CORE FEATURE)
# =========================
@api_view(['GET'])
def search_profiles(request):
    query = request.GET.get("q")

    if not query:
        return Response(
            {"status": "error", "message": "Query is required"},
            status=400
        )

    parsed = parse_query(query)

    # merge pagination params
    parsed.update({
        "page": request.GET.get("page"),
        "limit": request.GET.get("limit"),
        "sort_by": request.GET.get("sort_by"),
        "order": request.GET.get("order"),
    })

    if not parsed:
        return Response(
            {"status": "error", "message": "Unable to interpret query"},
            status=400
        )

    result = filter_profiles({**parsed, **request.GET})

    serializer = ProfileSerializer(result["data"], many=True)

    return Response({
        "status": "success",
        "page": result["page"],
        "limit": result["limit"],
        "total": result["total"],
        "data": serializer.data
    })