from app.conference.api.serializers.course import CourseSerializer
from rest_framework import serializers
from ...models import Conference


class ConferenceAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conference
        read_only_fields = ["id", "created_at", "updated_at", "number_of_slides"]
        fields = [
            "id",
            "created_at",
            "updated_at",
            "name",
            "description",
            "active",
            "course",
            "owner",
            "alert_to_owner",
            "number_of_slides",
        ]


class ConferenceSerializer(ConferenceAdminSerializer):
    course = CourseSerializer()
