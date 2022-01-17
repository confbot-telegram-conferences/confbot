from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = AutoCreatedField(db_index=True, verbose_name=_("Created at"))
    updated_at = AutoLastModifiedField(db_index=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True
