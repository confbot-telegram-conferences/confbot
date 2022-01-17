from app.conference.api.filters.conference import ConferenceFilter
from django.http.response import Http404
from app.conference.api.serializers.slide import SlideSerializer
from app.conference.models.slide import Slide
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from app.conference.api.serializers.user_conference import UserConferenceEvaluationSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.utils.paginator import Paginator
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from app.utils.permissions import IsBotPermission
from app.conference.api.serializers.conference import ConferenceAdminSerializer, ConferenceSerializer
from app.conference.tasks import download_zip_task, upload_zip_task
from app.conference.signals import start_conference, evaluated_conference
from ..models import Conference, UserConference


class ConferenceOwnerViewSet(ModelViewSet):
    queryset = Conference.objects.all()
    serializer_class = ConferenceAdminSerializer
    permission_classes = [IsBotPermission, IsAuthenticated]
    pagination_class = Paginator
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ["course"]
    search_fields = ["name"]

    def get_queryset(self):
        queryset = self.queryset.get_by_user(self.request.user).order_by("created_at")
        if "orphan_conferences" in self.request.query_params:
            queryset = queryset.filter(course__isnull=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=["post"], detail=False)
    def upload_zip_file(self, request, *args, **kwargs):
        upload_zip_task.apply_async(kwargs={"data": request.data, "user_id": request.user.id})
        return Response()

    @action(methods=["post"], detail=True)
    def download_zip_file(self, request, *args, **kwargs):
        conference: Conference = self.get_object()
        download_zip_task.apply_async(kwargs={"conference_id": conference.id, "chat_id": request.data.get("chat_id")})
        return Response()

    @action(methods=["post"], detail=True)
    def clear_slides(self, request, *args, **kwargs):
        conference: Conference = self.get_object()
        for slide in conference.slides.all():
            slide.delete()
        return Response()


class ConferenceViewSet(ReadOnlyModelViewSet):
    queryset = Conference.objects.all()
    permission_classes = [IsBotPermission, IsAuthenticated]
    serializer_class = ConferenceSerializer
    pagination_class = Paginator
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = ConferenceFilter
    search_fields = ["name"]

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.get_actives()
        return queryset.order_by("created_at")

    @action(url_path="by-position/(?P<position>[^/.]+)", methods=["get"], detail=True)
    def by_position(self, request, position, *args, **kwargs):
        position = int(position)
        conference: Conference = self.get_object()
        query = Slide.objects.order_by_position(conference=conference)
        if query.count() < position or position < 1:
            raise Http404()
        slide = query[position - 1]
        if position == 1:
            start_conference.send(self.__class__, conference=conference, user=request.user)
        return Response({"data": SlideSerializer(slide).data, "is_last": query.count() == position})

    @action(methods=["post"], detail=True)
    def evaluate(self, request, *args, **kwargs):
        conference: Conference = self.get_object()
        user_conference: UserConference = get_object_or_404(UserConference, conference=conference, user=request.user)
        serialice = UserConferenceEvaluationSerializer(instance=user_conference, data=request.data)
        if serialice.is_valid(raise_exception=True):
            user_conference = serialice.save()
            evaluated_conference.send(
                self.__class__, conference=conference, user=request.user, user_conference=user_conference
            )
        return Response()

    @action(methods=["get"], detail=True)
    def statistics(self, *args, **kwargs):
        data = UserConference.objects.statistics(conference=self.get_object())
        return Response(data)
