from app.conference.api.serializers.category import CategorySerializer
from app.conference.models.course import Course
from rest_framework import serializers


class CourseAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "number_of_conferences",
            "number_of_active_conferences",
        ]
        fields = [
            "id",
            "created_at",
            "updated_at",
            "name",
            "description",
            "category",
            "number_of_conferences",
            "number_of_active_conferences",
        ]


class CourseSerializer(CourseAdminSerializer):
    category = CategorySerializer()
