from app.conference.models.course import Course
from app.conference.models.conference import Conference
from app.users.models import User
from django.db.models import (
    BooleanField,
    OneToOneField,
    CharField,
    CASCADE,
    OuterRef,
    QuerySet,
    Count,
    IntegerField,
    Subquery,
    Q,
)
from django.db.models.functions import Coalesce
from app.utils.models import BaseModel
from django.utils.translation import gettext_lazy as _


class ChannelQuerySet(QuerySet):
    def get_by_user(self, user: User):
        return self.filter(owner=user)

    def get_public_channels(self):
        confereces = (
            Conference.objects.get_actives()
            .filter(course__isnull=True, owner=OuterRef("owner"))
            .annotate(c=Count("id"))
            .values("c")[:1]
        )
        courses = (
            Course.objects.get_with_active_conferences()
            .filter(owners=OuterRef("owner"))
            .annotate(c=Count("id"))
            .values("c")[:1]
        )
        return (
            self.filter(published=True)
            .annotate(
                conference_count=Coalesce(Subquery(confereces, output_field=IntegerField()), 0),
                course_count=Coalesce(Subquery(courses, output_field=IntegerField()), 0),
            )
            .filter(Q(conference_count__gt=0) | Q(course_count__gt=0))
        )


class Channel(BaseModel):
    name = CharField(_("Name of the Channel"), max_length=255)
    published = BooleanField(default=False)
    owner: User = OneToOneField(User, null=True, on_delete=CASCADE)

    objects = ChannelQuerySet.as_manager()

    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)
        self.previous_published = self.published

    def __str__(self):
        return f"{self.name} ({self.owner})"

    def save(self, *args, **kwargs):
        result = super(Channel, self).save(*args, **kwargs)
        self.previous_published = self.published
        return result
