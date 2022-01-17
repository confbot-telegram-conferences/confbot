from app.conference.models.channel import Channel
from django_filters import rest_framework as filters
from django_filters.filters import BooleanFilter, ModelChoiceFilter
from app.conference.models import Conference


class ConferenceFilter(filters.FilterSet):
    channel = ModelChoiceFilter(queryset=Channel.objects.all(), field_name="owner__channel")
    orphan_conferences = BooleanFilter(field_name="course", lookup_expr="isnull", exclude=False)

    class Meta:
        model = Conference
        fields = ["course", "channel", "orphan_conferences"]
