from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EnterpriseConfig(AppConfig):
    name = "app.enterprise"
    verbose_name = _("Users")
