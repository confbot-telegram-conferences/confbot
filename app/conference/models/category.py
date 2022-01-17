from django.db.models import CharField
from app.utils.models import BaseModel
from django.utils.translation import gettext_lazy as _


class Category(BaseModel):
    name = CharField(_("Name"), max_length=255)

    def __str__(self) -> str:
        return self.name
