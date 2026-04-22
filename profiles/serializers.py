from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Profile
        fields = [
            "id",
            "name",
            "gender",
            "gender_probability",
            "age",
            "age_group",
            "country_id",
            "country_name",
            "country_probability",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "gender",
            "gender_probability",
            "age",
            "age_group",
            "country_id",
            "country_name",
            "country_probability",
            "created_at",
        ]

class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "gender", "age", "age_group", "country_id"]

class ProfileCreateSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate_name(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError("Name is required")

        if not isinstance(value, str):
            raise serializers.ValidationError("Name must be a string")

        return value