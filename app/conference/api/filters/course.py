from app.conference.models.channel import Channel
from django_filters import rest_framework as filters
from django_filters.filters import ModelChoiceFilter
from app.conference.models import Course


class CourseFilter(filters.FilterSet):
    channel = ModelChoiceFilter(queryset=Channel.objects.all(), field_name="owners__channel")

    class Meta:
        model = Course
        fields = ["category", "channel"]
