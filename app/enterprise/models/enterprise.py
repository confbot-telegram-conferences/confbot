from django.db.models import CharField, ManyToManyField
from django.utils.translation import gettext_lazy as _
from app.utils.models import BaseModel
from app.users.models import User


class Enterprise(BaseModel):
    name = CharField(_("Name of Enterprise"), max_length=255)
    members = ManyToManyField(User, through="UserEnterprise", related_name="enterprises")
