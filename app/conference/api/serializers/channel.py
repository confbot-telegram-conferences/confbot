from rest_framework import serializers
from ...models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    conference_count = serializers.SerializerMethodField(read_only=True)
    course_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Channel
        read_only_fields = ["id", "created_at", "updated_at"]
        fields = [
            "id",
            "created_at",
            "updated_at",
            "name",
            "published",
            "conference_count",
            "course_count",
        ]

    def get_conference_count(self, obj):
        return getattr(obj, "conference_count", 0)

    def get_course_count(self, obj):
        return getattr(obj, "course_count", 0)
