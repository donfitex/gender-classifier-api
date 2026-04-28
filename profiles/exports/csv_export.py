import csv
from django.http import HttpResponse
from datetime import datetime

def export_profiles_csv(qs):
    response = HttpResponse(content_type="text/csv")

    filename = f"profiles_{datetime.utcnow().isoformat()}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    writer.writerow([
        "id", "name", "gender", "gender_probability",
        "age", "age_group", "country_id",
        "country_name", "country_probability", "created_at"
    ])

    for p in qs:
        writer.writerow([
            p.id, p.name, p.gender, p.gender_probability,
            p.age, p.age_group, p.country_id,
            p.country_name, p.country_probability, p.created_at
        ])

    return response