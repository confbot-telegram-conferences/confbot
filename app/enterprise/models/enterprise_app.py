from django.db.models import CharField, URLField, OneToOneField, CASCADE
from app.utils.models import BaseModel
from django.utils.translation import gettext_lazy as _
from .enterprise import Enterprise


class EnterpriseApp(BaseModel):
    apk_key = CharField(_("App Namekey of Enterprise"), max_length=255)
    web_hook = URLField(_("Url from enterprise web hook"), null=True, blank=True)
    enterprise = OneToOneField(Enterprise, on_delete=CASCADE)
