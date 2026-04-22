from ..models import Profile


def apply_filters(qs, params):
    if params.get("gender"):
        qs = qs.filter(gender__iexact=params["gender"])

    if params.get("age_group"):
        qs = qs.filter(age_group__iexact=params["age_group"])

    if params.get("country_id"):
        qs = qs.filter(country_id__iexact=params["country_id"])

    if params.get("min_age"):
        qs = qs.filter(age__gte=int(params["min_age"]))

    if params.get("max_age"):
        qs = qs.filter(age__lte=int(params["max_age"]))

    if params.get("min_gender_probability"):
        qs = qs.filter(gender_probability__gte=float(params["min_gender_probability"]))

    if params.get("min_country_probability"):
        qs = qs.filter(country_probability__gte=float(params["min_country_probability"]))

    return qs


def apply_sorting(qs, sort_by, order):
    allowed_fields = ["age", "created_at", "gender_probability"]

    if sort_by:
        if sort_by not in allowed_fields:
            raise ValueError("Invalid sort field")

        field = sort_by
        if order == "desc":
            field = f"-{field}"

        qs = qs.order_by(field)

    return qs


def paginate(qs, page, limit):
    page = int(page or 1)
    limit = min(int(limit or 10), 50)

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