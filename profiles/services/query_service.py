from ..models import Profile

def safe_int(value):
    try:
        return int(value)
    except:
        return None

def apply_filters(qs, params):
    if params.get("gender"):
        qs = qs.filter(gender__iexact=params["gender"])

    if params.get("age_group"):
        qs = qs.filter(age_group__iexact=params["age_group"])

    if params.get("country_id"):
        qs = qs.filter(country_id__iexact=params["country_id"])

    min_age = safe_int(params.get("min_age"))
    max_age = safe_int(params.get("max_age"))


    if params.get("min_age") and min_age is None:
        raise ValueError("Invalid query parameters")

    if params.get("max_age") and max_age is None:
        raise ValueError("Invalid query parameters")

    if min_age is not None:
        qs = qs.filter(age__gte=min_age)

    if max_age is not None:
        qs = qs.filter(age__lte=max_age)

    return qs



ALLOWED_FIELDS = ["age", "created_at", "gender_probability"]

def apply_sorting(qs, sort_by, order):

    if sort_by and sort_by not in ALLOWED_FIELDS:
        raise ValueError("Invalid query parameters")

    if sort_by:
        field = sort_by
        if order == "desc":
            field = f"-{field}"
        qs = qs.order_by(field)

    return qs


def paginate(qs, page, limit):
    try:
        page = int(page or 1)
        limit = int(limit or 10)
    except:
        raise ValueError("Invalid query parameters")

    if page < 1 or limit < 1:
        raise ValueError("Invalid query parameters")

    limit = min(limit, 50)

    start = (page - 1) * limit
    end = start + limit

    return qs[start:end], qs.count(), page, limit


# MAIN ENTRY (THIS IS WHAT VIEW USES)
def filter_profiles(params):
    qs = Profile.objects.all()

    # Filtering
    qs = apply_filters(qs, params)

    # Sorting
    qs = apply_sorting(
        qs,
        params.get("sort_by"),
        params.get("order")
    )

    # Pagination
    data, total, page, limit = paginate(
        qs,
        params.get("page"),
        params.get("limit")
    )

    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit
    }