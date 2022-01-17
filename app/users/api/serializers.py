from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "external_id",
            "lenguage_code",
            "is_bot",
        ]

        extra_kwargs = {"url": {"view_name": "api:user-detail", "lookup_field": "username"}}
