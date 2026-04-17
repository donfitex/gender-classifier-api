import requests
import logging
from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


# =========================
# CLASSIFY (Stage 0)
# =========================
@api_view(['GET'])
def classify_name(request):
    name = request.GET.get('name')

    if name is None or str(name).strip() == "":
        return Response(
            {"status": "error", "message": "Name is required"},
            status=400
        )

    if not isinstance(name, str):
        return Response(
            {"status": "error", "message": "Name must be a string"},
            status=422
        )

    name = name.strip().lower()

    try:
        res = requests.get(f"https://api.genderize.io?name={name}", timeout=3)
        res.raise_for_status()
        data = res.json()

        gender = data.get("gender")
        probability = data.get("probability")
        count = data.get("count")

        if gender is None or count == 0:
            return Response(
                {"status": "error", "message": "Genderize returned an invalid response"},
                status=502
            )

        is_confident = (
            probability is not None and
            count is not None and
            probability >= 0.7 and
            count >= 100
        )

        return Response({
            "status": "success",
            "data": {
                "name": name,
                "gender": gender,
                "probability": probability,
                "sample_size": count,
                "is_confident": is_confident,
                "processed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
        })

    except requests.exceptions.RequestException:
        return Response(
            {"status": "error", "message": "External API error"},
            status=502
        )

