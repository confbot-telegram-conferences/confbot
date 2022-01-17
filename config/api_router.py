from app.conference.api.channel import ChannelOwnerViewSet, ChannelViewSet
from app.metric.api.group_channel import GroupChannelViewSet
from app.utils.sentry_ckeck import sentry_check
from app.conference.api.course import CourceViewSet, CourseOwnerViewSet
from app.conference.api.category import CategpryViewSet
from rest_framework_nested import routers
from django.conf.urls import url, include
from app.conference.api.slide import SlideOwnerViewSet, SlideViewSet
from app.conference.api.conference import ConferenceOwnerViewSet, ConferenceViewSet
from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path

from app.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)

router.register("categories", CategpryViewSet)

router.register("admin/group-channels", GroupChannelViewSet)

# Courses
router.register("courses", CourceViewSet)
router.register("conferences", ConferenceViewSet)
router.register("admin/courses", CourseOwnerViewSet)
router.register("admin/conferences", ConferenceOwnerViewSet)
router.register("channels", ChannelViewSet)

# Conference admin
conference_admin_router = routers.NestedSimpleRouter(router, r"admin/conferences", lookup="conference")
conference_admin_router.register(r"slides", SlideOwnerViewSet, basename="conference-slide")

# Conference
conference_router = routers.NestedSimpleRouter(router, r"conferences", lookup="conference")
conference_router.register(r"slides", SlideViewSet, basename="conference-slide")

app_name = "api"
urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^", include(conference_router.urls)),
    url(r"^", include(conference_admin_router.urls)),
    path("sentry-check/<str:pk>/", sentry_check, name="sentry-check"),
    path("admin/channel", ChannelOwnerViewSet.as_view(), name="channel-admin"),
]
