from app.utils.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from app.conference.models import Channel
from app.conference.api.serializers.channel import ChannelSerializer
from rest_framework.permissions import IsAuthenticated
from app.utils.permissions import IsBotPermission
from rest_framework.response import Response


class ChannelOwnerViewSet(APIView):
    queryset = Channel.objects.all()
    permission_classes = [IsBotPermission, IsAuthenticated]

    def get_queryset(self):
        return self.queryset.get_by_user(self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            instance = Channel.objects.get(owner=request.user)
        except Channel.DoesNotExist:
            instance = Channel(owner=request.user)
            instance.save()
        serializer = ChannelSerializer(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = Channel.objects.get(owner=request.user)
        serializer = ChannelSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChannelViewSet(ReadOnlyModelViewSet):
    queryset = Channel.objects.all()
    permission_classes = [IsBotPermission, IsAuthenticated]
    serializer_class = ChannelSerializer
    pagination_class = Paginator

    def get_queryset(self):
        queryset = self.queryset
        return queryset.get_public_channels().order_by("-updated_at")
