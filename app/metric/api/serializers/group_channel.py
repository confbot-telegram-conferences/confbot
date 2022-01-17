from rest_framework import serializers
from ...models import GroupChannel


class GroupChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChannel
        read_only_fields = ["id", "created_at", "updated_at"]
        fields = [
            "id",
            "created_at",
            "updated_at",
            "external_id",
            "title",
            "type",
            "active",
            "data",
        ]
