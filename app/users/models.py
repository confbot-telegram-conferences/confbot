from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, BooleanField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from app.utils.models import BaseModel


class User(AbstractUser, BaseModel):
    """Default user for confbot."""

    external_id = CharField(_("External id"), db_index=True, blank=True, null=True, max_length=255)
    lenguage_code = CharField(_("Lenguage code"), default="en", blank=True, max_length=255)
    is_bot = BooleanField(_("Lenguage code"), blank=True, default=False)
    first_name = CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = CharField(_("last name"), max_length=150, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} <{self.username}>"

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
