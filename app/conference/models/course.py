from functools import reduce
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, CharField, TextField, ManyToManyField, ForeignKey, SET_NULL, QuerySet, Count
from app.conference.models.category import Category
from app.users.models import User
from app.utils.models import BaseModel


class ManagerQuerySet(QuerySet):
    def get_by_user(self, user: User):
        return self.filter(owners=user)

    def get_with_active_conferences(self):
        return self.annotate(num_conferences=Count("conferences", filter=Q(conferences__active=True))).filter(
            num_conferences__gt=0
        )


class Course(BaseModel):
    name = CharField(_("Name"), max_length=255)
    description = TextField(default="", blank=True)
    owners = ManyToManyField(User, related_name="courses")
    category = ForeignKey(Category, null=True, on_delete=SET_NULL)

    objects = ManagerQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    @property
    def number_of_conferences(self):
        return self.conferences.count()

    @property
    def number_of_active_conferences(self):
        return self.conferences.filter(active=True).count()

    @property
    def files(self):
        return reduce(lambda acc, conference: acc + conference.files, self.conferences.all(), [])
