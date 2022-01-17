from rest_framework import serializers
from ...models import Slide


class SlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slide
        read_only_fields = ["id", "created_at", "updated_at", "position", "conference"]
        fields = [
            "id",
            "created_at",
            "updated_at",
            "text",
            "image_id",
            "voice_id",
            "position",
            "conference_number_of_slides",
            "conference",
        ]
