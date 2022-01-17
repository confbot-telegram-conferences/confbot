from app.conference.api.serializers.category import CategorySerializer
from rest_framework.permissions import IsAuthenticated
from app.utils.permissions import IsBotPermission
from app.conference.models.category import Category
from rest_framework.viewsets import ReadOnlyModelViewSet


class CategpryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsBotPermission, IsAuthenticated]
    serializer_class = CategorySerializer
