import json
from rest_framework.authentication import BaseAuthentication
from app.users.models import User


class BotUserBackend(BaseAuthentication):
    def authenticate(self, request):
        data = json.loads(request.META.get("HTTP_AUTHORIZATION"))
        user_id = data["user_id"] if "user_id" in data else None
        try:
            return (User.objects.get(pk=user_id), user_id) if user_id else None
        except User.DoesNotExist:
            return None
