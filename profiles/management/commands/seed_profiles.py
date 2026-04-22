import json
from django.core.management.base import BaseCommand
from profiles.models import Profile


class Command(BaseCommand):
    help = "Seed database with 2026 profiles (idempotent)"

    def handle(self, *args, **kwargs):
        file_path = "profiles/data/seed_profiles.json"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("Dataset file not found"))
            return

        profiles = data.get("profiles", [])

        created = 0
        skipped = 0

        for item in profiles:
            name = item.get("name")

            if not name:
                continue

            name = name.strip().lower()

            # ✅ Idempotency
            if Profile.objects.filter(name=name).exists():
                skipped += 1
                continue

            Profile.objects.create(
                name=name,
                gender=item.get("gender"),
                gender_probability=float(item.get("gender_probability", 0)),
                age=int(item.get("age", 0)),
                age_group=item.get("age_group"),
                country_id=item.get("country_id"),
                country_name=item.get("country_name"),
                country_probability=float(item.get("country_probability", 0)),
            )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding complete: {created} created, {skipped} skipped"
            )
        )