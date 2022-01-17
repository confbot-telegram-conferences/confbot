from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ConferenceConfig(AppConfig):
    name = "app.conference"
    verbose_name = _("Conferences")

    def ready(self) -> None:
        import app.conference.listener  # noqa
