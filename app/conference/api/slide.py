from uuid import UUID
from django.http.response import HttpResponseNotFound
from rest_framework.permissions import IsAuthenticated
from app.conference.models.user_conference import UserConference
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from app.utils.telegram import FileBigException, get_bot, send_photo_by_id, send_voice_by_id
from app.utils.paginator import Paginator
from app.utils.permissions import IsBotPermission
from app.conference.models.conference import Conference
from app.conference.api.serializers.slide import SlideSerializer
from ..models import Slide


class SendFilesMixin:
    @action(methods=["post"], detail=True)
    def send_image(self, request, *args, **kwargs):
        object: Slide = self.get_object()
        if not object.image_id:
            raise HttpResponseNotFound
        bot = get_bot()
        chat_id = request.data["chat_id"]
        message = send_photo_by_id(bot=bot, chat_id=chat_id, file_id=object.image_id)
        return Response({"message_id": message["message_id"]})

    @action(methods=["post"], detail=True)
    def send_audio(self, request, *args, **kwargs):
        object: Slide = self.get_object()
        if not object.voice_id:
            raise HttpResponseNotFound
        bot = get_bot()
        chat_id = request.data["chat_id"]
        message = send_voice_by_id(bot=bot, chat_id=chat_id, file_id=object.voice_id)
        return Response({"message_id": message["message_id"]})


class SlideOwnerViewSet(SendFilesMixin, ModelViewSet):
    queryset = Slide.objects.all()
    serializer_class = SlideSerializer
    permission_classes = [IsBotPermission, IsAuthenticated]
    pagination_class = Paginator

    def _get_conference(self):
        return get_object_or_404(Conference, owner=self.request.user, id=UUID(self.kwargs["conference_pk"]))

    def get_queryset(self):
        return self.queryset.select_related("conference").order_by_position(conference=self._get_conference())

    def perform_create(self, serializer):
        serializer.save(conference=self._get_conference())

    @action(methods=["post"], detail=True)
    def save_image(self, request, *args, **kwargs):
        object: Slide = self.get_object()
        object.save_image_data(request.data)
        object.save()
        return Response()

    @action(methods=["post"], detail=True)
    def save_audio(self, request, *args, **kwargs):
        try:
            object: Slide = self.get_object()
            object.save_voice_data(request.data)
            object.save()
            return Response()
        except FileBigException as e:
            return Response(data=e.message, status=400)


class SlideViewSet(SendFilesMixin, ReadOnlyModelViewSet):
    queryset = Slide.objects.all()
    pagination_class = Paginator
    serializer_class = SlideSerializer
    permission_classes = [IsBotPermission, IsAuthenticated]

    def get_queryset(self):
        conference = get_object_or_404(Conference, id=UUID(self.kwargs["conference_pk"]))
        return self.queryset.select_related("conference").order_by_position(conference=conference)

    @action(methods=["post"], detail=True)
    def set_as_viewed(self, request, *args, **kwargs):
        slide: Slide = self.get_object()
        UserConference.objects.update_or_create_with_slide(
            conference=slide.conference,
            user=request.user,
            slide=slide,
        )
        return Response()
