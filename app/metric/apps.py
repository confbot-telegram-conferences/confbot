from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MetricConfig(AppConfig):
    name = "app.metric"
    verbose_name = _("Metric")
