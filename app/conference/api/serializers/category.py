from rest_framework import serializers
from app.conference.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        read_only_fields = ["id", "created_at", "updated_at"]
        fields = ["id", "created_at", "updated_at", "name"]
