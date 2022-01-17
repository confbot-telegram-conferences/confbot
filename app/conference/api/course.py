from app.conference.api.filters.course import CourseFilter
from app.utils.paginator import Paginator
from app.conference.api.serializers.course import CourseAdminSerializer, CourseSerializer
from rest_framework.permissions import IsAuthenticated
from app.utils.permissions import IsBotPermission
from app.conference.models.course import Course
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class CourseOwnerViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseAdminSerializer
    permission_classes = [IsBotPermission, IsAuthenticated]
    pagination_class = Paginator

    def get_queryset(self):
        return self.queryset.get_by_user(self.request.user).order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(owners=[self.request.user])


class CourceViewSet(ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    permission_classes = [IsBotPermission, IsAuthenticated]
    serializer_class = CourseSerializer
    pagination_class = Paginator
    filterset_class = CourseFilter

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.get_with_active_conferences()
        return queryset.order_by("created_at")
