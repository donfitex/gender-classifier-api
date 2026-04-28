from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Profile
from .serializers import (
    ProfileSerializer,
    ProfileCreateSerializer,
    ProfileListSerializer
)

from .services.profile_service import create_profile
from .services.query_service import apply_filters, apply_sorting
from .services.nlp_service import parse_query

from .utils.versioning import check_version
from .utils.pagination import paginate_queryset, build_links

from .exports.csv_export import export_profiles_csv


# =========================
# LIST + CREATE
# =========================
@api_view(['GET', 'POST'])
def profiles(request):

    # -------------------------
    # API VERSION CHECK
    # -------------------------
    if not check_version(request):
        return Response(
            {"status": "error", "message": "API version header required"},
            status=400
        )

    # =========================
    # GET → LIST PROFILES
    # =========================
    if request.method == 'GET':
        try:
            qs = Profile.objects.all()

            # -------------------------
            # FILTERING
            # -------------------------
            qs = apply_filters(qs, request.GET)

            # -------------------------
            # SORTING
            # -------------------------
            sort_by = request.GET.get("sort_by")
            order = request.GET.get("order")
            qs = apply_sorting(qs, sort_by, order)

            # -------------------------
            # CSV EXPORT
            # -------------------------
            if request.GET.get("format") == "csv":
                return export_profiles_csv(qs)

            # -------------------------
            # PAGINATION
            # -------------------------
            data, meta = paginate_queryset(qs, request)

            serializer = ProfileListSerializer(data, many=True)

            links = build_links(
                request,
                meta["page"],
                meta["limit"],
                meta["total_pages"]
            )

            return Response({
                "status": "success",
                **meta,
                "links": links,
                "data": serializer.data
            })

        except ValueError:
            return Response(
                {"status": "error", "message": "Invalid query parameters"},
                status=400
            )


    # =========================
    # POST → CREATE PROFILE (ADMIN ONLY)
    # =========================
    elif request.method == 'POST':

        # -------------------------
        # ROLE CHECK
        # -------------------------
        if not hasattr(request, "user") or request.user.role != "admin":
            return Response(
                {"status": "error", "message": "Forbidden"},
                status=403
            )

        serializer = ProfileCreateSerializer(data=request.data)

        if not serializer.is_valid():
            error_msg = list(serializer.errors.values())[0][0]

            # 422 → invalid type
            if "string" in str(error_msg).lower():
                return Response(
                    {"status": "error", "message": error_msg},
                    status=422
                )

            return Response(
                {"status": "error", "message": error_msg},
                status=400
            )

        name = serializer.validated_data["name"]

        # -------------------------
        # SERVICE CALL
        # -------------------------
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

    # -------------------------
    # API VERSION CHECK
    # -------------------------
    if not check_version(request):
        return Response(
            {"status": "error", "message": "API version header required"},
            status=400
        )

    try:
        profile = Profile.objects.get(id=id)

        # -------- GET --------
        if request.method == 'GET':
            return Response({
                "status": "success",
                "data": ProfileSerializer(profile).data
            })

        # -------- DELETE (ADMIN ONLY) --------
        elif request.method == 'DELETE':

            if not hasattr(request, "user") or request.user.role != "admin":
                return Response(
                    {"status": "error", "message": "Forbidden"},
                    status=403
                )

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

    # -------------------------
    # API VERSION CHECK
    # -------------------------
    if not check_version(request):
        return Response(
            {"status": "error", "message": "API version header required"},
            status=400
        )

    q = request.GET.get("q")

    if not q:
        return Response(
            {"status": "error", "message": "Query is required"},
            status=400
        )

    # -------------------------
    # NLP PARSING
    # -------------------------
    filters = parse_query(q)

    if not filters:
        return Response(
            {"status": "error", "message": "Unable to interpret query"},
            status=400
        )

    try:
        qs = Profile.objects.all()

        # apply parsed filters
        qs = apply_filters(qs, filters)

        # -------------------------
        # SORTING
        # -------------------------
        sort_by = request.GET.get("sort_by")
        order = request.GET.get("order")
        qs = apply_sorting(qs, sort_by, order)

        # -------------------------
        # PAGINATION
        # -------------------------
        data, meta = paginate_queryset(qs, request)

        serializer = ProfileListSerializer(data, many=True)

        links = build_links(
            request,
            meta["page"],
            meta["limit"],
            meta["total_pages"]
        )

        return Response({
            "status": "success",
            **meta,
            "links": links,
            "data": serializer.data
        })

    except ValueError:
        return Response(
            {"status": "error", "message": "Invalid query parameters"},
            status=400
        )