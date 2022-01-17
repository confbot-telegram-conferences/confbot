from app.conference.models.conference import Conference
from app.utils.models import BaseModel
from django.db.models import CharField, ManyToManyField, BooleanField
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _


class GroupChannel(BaseModel):
    external_id = CharField(_("External id"), max_length=255)
    title = CharField(_("Title"), max_length=255)
    type = CharField(_("Type"), max_length=255)
    data = JSONField(null=True, blank=True)
    active = BooleanField(_("Active"), default=True)
    conferences = ManyToManyField(Conference, related_name="group_channels")

    def __str__(self) -> str:
        return f"{self.title} ({self.type})"
