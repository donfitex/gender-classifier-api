import requests
import logging
from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

#logger setup
logger = logging.getLogger(__name__)

@api_view(['GET'])
def classify_name(request):
    name = request.GET.get('name')

    #Input Validation
    if name is None or name.strip() == "":
        logger.warning("Request missing 'name' parameter")
        return Response(
            {"status": "error", "message": "Name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not isinstance(name, str):
        logger.warning(f"Invalid name type received: {type(name)}")
        return Response(
            {"status": "error", "message": "Name must be a string"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    #Normal input
    name =name.strip().lower()

    try:
        #External API call with timeout
        url = f"https://api.genderize.io?name={name}"
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        data = response.json()
        gender = data.get('gender')
        probability = data.get('probability')
        count = data.get('count')

        #Edge case handling
        if gender is None or count == 0:
            logger.info(f"No prediction for name: {name}")
            return Response(
                {"status": "error", "message": "No prediction for the provided name"},
                status=status.HTTP_200_OK
            )
        
        #Processing
        is_confident = (
            probability is not None and 
            count is not None and
            probability >= 0.7 and 
            count >= 100
        )
        processed_data = {
            "name": name,
                "gender": gender,
                "probability": probability,
                "sample_size": count,
                "is_confident": is_confident,
                "processed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        logger.info(f"Successful classification for: {name}")
        return Response(
            {   "status": "success",
                "data": processed_data 
            },
            status=status.HTTP_200_OK
        )

    except requests.exceptions.Timeout:
        logger.error("Genderize API timeout")
        return Response(
            {"status": "error", "message": "External API timeout"},
            status=status.HTTP_502_BAD_GATEWAY
        )
    
    except requests.exceptions.ReadTimeout as e:
        logger.error(f"External API error: {str(e)}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )