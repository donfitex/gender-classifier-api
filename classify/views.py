import requests
import logging
from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Profile

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
        logger.error("External API timeout")
        return Response(
            {"status": "error", "message": "External API timeout"},
            status=status.HTTP_502_BAD_GATEWAY
    )

    except requests.exceptions.RequestException as e:
        logger.error(f"External API error: {str(e)}")
        return Response(
            {"status": "error", "message": "External API error"},
            status=status.HTTP_502_BAD_GATEWAY
        )
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
# Additional helper functions for processing data
def get_age_group(age):
    if age <= 12:
        return "child"
    elif 13 <= age <= 19:
        return "teenager"
    elif 20 <= age <= 59:
        return "adult"
    else:
        return "senior"
    

def get_top_country(countries):
    valid = [c for c in countries if 'country_id' in c and 'probability' in c]
    if not valid:
        return None, None
    
    top_country = max(valid, key=lambda x: x['probability'])
    return top_country['country_id'], top_country['probability']


# Serialize profile for response and return
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


@api_view(['POST'])
def create_profile(request):
    name = request.data.get("name")

    # Endpoint to create a profile with validation
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

    # Add idempotency to check if profile already exists
    existing_profile = Profile.objects.filter(name=name).first()
    if existing_profile:
        return Response(
            {"status": "success", "message": "Profile already exists", "data": serialize_profile(existing_profile)},
            status=200
        )


    #Integrate external APIs
    try:
        gender_res = requests.get(f"https://api.genderize.io?name={name}", timeout=2)
        gender_res.raise_for_status()
        gender_data = gender_res.json()

        age_res = requests.get(f"https://api.agify.io?name={name}", timeout=2)
        age_res.raise_for_status()
        age_data = age_res.json()

        nation_res = requests.get(f"https://api.nationalize.io?name={name}", timeout=2)
        nation_res.raise_for_status()
        nation_data = nation_res.json()


        #Data extraction, validation, and processing logic
        # Gender
        gender = gender_data.get("gender")
        probability = gender_data.get("probability")
        count = gender_data.get("count")

        if gender is None or count == 0:
            return Response(
                {"status": "error", "message": "No gender data available"},
                status=404
            )

        # Age
        age = age_data.get("age")
        if age is None:
            return Response(
                {"status": "error", "message": "No age data available"},
                status=404
            )

        age_group = get_age_group(age)

        # Country
        countries = nation_data.get("country", [])
        country_id, country_probability = get_top_country(countries)

        if not country_id:
            return Response(
                {"status": "error", "message": "No country data available"},
                status=404
            )
        
        # Save to database
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
    
    # Handle external API errors gracefully
    except requests.exceptions.Timeout:
        logger.error("External API timeout")
        return Response(
            {"status": "error", "message": "External API timeout"},
            status=status.HTTP_502_BAD_GATEWAY
    )

    except requests.exceptions.RequestException as e:
        logger.error(f"External API error: {str(e)}")
        return Response(
            {"status": "error", "message": "External API error"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )