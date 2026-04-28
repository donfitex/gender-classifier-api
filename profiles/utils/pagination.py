def paginate_queryset(qs, request):
    page = int(request.GET.get("page", 1))
    limit = min(int(request.GET.get("limit", 10)), 50)

    total = qs.count()
    start = (page - 1) * limit
    end = start + limit

    data = qs[start:end]

    total_pages = (total + limit - 1) // limit

    return data, {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }

# Helper to build pagination links
def build_links(request, page, limit, total_pages):
    base = request.path

    return {
        "self": f"{base}?page={page}&limit={limit}",
        "next": f"{base}?page={page+1}&limit={limit}" if page < total_pages else None,
        "prev": f"{base}?page={page-1}&limit={limit}" if page > 1 else None,
    }
