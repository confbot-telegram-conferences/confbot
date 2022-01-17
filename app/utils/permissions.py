import json
from functools import reduce
from rest_framework.permissions import BasePermission
from django.conf import settings


class IsBotPermission(BasePermission):
    def has_permission(self, request, view):
        data = json.loads(request.META.get("HTTP_AUTHORIZATION"))
        return "app_key" in data and settings.BOT_SECRET_KEY == data["app_key"]


def is_owner_permission(field="owner", actions=None):
    actions = actions if actions else ["list", "retrieve"]

    class IsOwnerPermission(BasePermission):
        def has_object_permission(self, request, view, obj):
            user = reduce(lambda a, c: getattr(a, c), field.split("."), obj)
            if view.action in actions:
                return True
            return user == request.user

    return IsOwnerPermission
