from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete
from django.db.models import CharField, TextField, ForeignKey, IntegerField, CASCADE, QuerySet, F
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _
from app.utils.models import BaseModel
from . import Conference


class ManagerQuerySet(QuerySet):
    def get_by_conference(self, conference: Conference):
        return self.filter(conference=conference)

    def get_last_position(self, conference: Conference):
        item: Slide = self.get_by_conference(conference=conference).order_by("-position").first()
        return item.position if item else 0

    def move_position(self, position, conference: Conference):
        self.get_by_conference(conference=conference).filter(position__gt=position).update(position=F("position") - 1)

    def order_by_position(self, conference: Conference):
        return self.get_by_conference(conference=conference).order_by("position")

    def get_by_position(self, conference: Conference, position):
        return self.get_by_conference(conference=conference).filter(position=position).first()

    def get_or_create_by_position(self, conference: Conference, position):
        slide = self.get_by_position(conference=conference, position=position)
        if not slide:
            slide = self.model(conference=conference, position=position)
        return slide


class Slide(BaseModel):
    text = TextField(_("Text"), default="", blank=True, null=True)
    image = CharField(_("Image"), max_length=255, null=True, blank=True)
    image_id = CharField(_("Image Id"), max_length=255, null=True, blank=True)
    image_data = JSONField(verbose_name=_("Image Data"), default=dict, null=True, blank=True)
    voice = CharField(_("Voice"), max_length=255, null=True, blank=True)
    voice_id = CharField(_("Voice Id"), max_length=255, null=True, blank=True)
    voice_data = JSONField(verbose_name=_("Voice Data"), default=dict, null=True, blank=True)
    position = IntegerField(_("Position"), default=1)
    conference = ForeignKey(Conference, related_name="slides", on_delete=CASCADE)

    objects: ManagerQuerySet = ManagerQuerySet.as_manager()

    def __init__(self, *args, **kwargs):
        super(Slide, self).__init__(*args, **kwargs)
        self.original_voice = self.voice
        self.original_image = self.image

    @property
    def conference_number_of_slides(self):
        return self.conference.slides.count()

    def __str__(self) -> str:
        return self.text if self.text else ""

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if not self.text and not self.image_id and not self.voice_id:
            raise ValidationError("It is needed to pass text, image or voice")

    @property
    def files(self):
        files = []
        if self.image:
            files += [self.image]
        if self.voice:
            files += [self.voice]
        return files

    @property
    def files_changed(self):
        files = []
        if self.image and self.original_image and self.image != self.original_image:
            files += [self.original_image]
        if self.voice and self.original_voice and self.voice != self.original_voice:
            files += [self.original_voice]
        return files

    def save_image_data(self, data):
        self.image_id = data["file_id"]
        self.image_data = data
        return self

    def save_voice_data(self, data):
        self.voice_id = data["file_id"]
        self.voice_data = data
        return self


@receiver(pre_save, sender=Slide)
def _set_position(sender, instance, *args, **kwargs):
    if instance._state.adding:
        instance.position = 1 + Slide.objects.get_last_position(conference=instance.conference)


@receiver(pre_delete, sender=Slide)
def _move_position(sender, instance, *args, **kwargs):
    Slide.objects.move_position(position=instance.position, conference=instance.conference)
