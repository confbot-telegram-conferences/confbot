from functools import reduce
from app.conference.models.course import Course
from django.db.models import CharField, TextField, ForeignKey, SET_NULL, QuerySet
from django.db.models.fields import BooleanField
from django.utils.translation import gettext_lazy as _
from app.utils.models import BaseModel
from app.users.models import User


class ConferenceQuerySet(QuerySet):
    def get_by_user(self, user: User):
        return self.filter(owner=user)

    def get_actives(self):
        return self.filter(active=True)

    def get_by_course(self, course: Course):
        return self.filter(course=course)


class Conference(BaseModel):
    name = CharField(_("Name of Conference"), max_length=255)
    description = TextField(_("Description"), default="", blank=True, null=True)
    owner: User = ForeignKey(User, null=True, on_delete=SET_NULL)
    active = BooleanField(default=False)
    alert_to_owner = BooleanField(default=True)
    course = ForeignKey(Course, null=True, blank=True, on_delete=SET_NULL, related_name="conferences")

    objects: ConferenceQuerySet = ConferenceQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name if self.name else ""

    @property
    def number_of_slides(self):
        return self.slides.count()

    @property
    def files(self):
        return reduce(lambda acc, slide: acc + slide.files, self.slides.all(), [])
