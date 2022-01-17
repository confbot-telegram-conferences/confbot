from rest_framework.generics import get_object_or_404
from app.conference.models.conference import Conference
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.utils.permissions import IsBotPermission
from app.metric.api.serializers.group_channel import GroupChannelSerializer
from app.metric.models.group_channel import GroupChannel
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action


class GroupChannelViewSet(CreateModelMixin, GenericViewSet):
    queryset = GroupChannel.objects.all()
    serializer_class = GroupChannelSerializer
    permission_classes = [IsBotPermission, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            object: GroupChannel = GroupChannel.objects.get(external_id=serializer.data["external_id"])
            object.active = True
            object.save()
            return Response(self.get_serializer(object).data, status=status.HTTP_200_OK)
        except GroupChannel.DoesNotExist:
            return super().create(request, *args, **kwargs)

    @action(url_path="get_by_external_id/(?P<external_id>[^/.]+)", methods=["get"], detail=False)
    def get_by_external_id(self, request, external_id, *args, **kwargs):
        object = get_object_or_404(GroupChannel, external_id=external_id)
        serializer = self.get_serializer(object)
        return Response(serializer.data)

    @action(methods=["post"], detail=True)
    def desactive(self, request, *args, **kwargs):
        object: GroupChannel = self.get_object()
        object.active = False
        object.save()
        return Response()

    @action(methods=["post"], detail=True)
    def start_conference(self, request, *args, **kwargs):
        object: GroupChannel = self.get_object()
        conference: Conference = get_object_or_404(Conference, pk=request.data["conference_id"])
        object.conferences.add(conference)
        object.save()
        return Response()
