from app.conference.models import UserConference, Channel, Conference, Slide
from app.utils.telegram import get_bot, send_message
from app.conference.tasks import remove_files_in_bots
from django.db.models.signals import post_delete, post_save
from app.conference.signals import start_conference, evaluated_conference
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from app.users.models import User
from telegram.parsemode import ParseMode


@receiver(post_delete, sender=Slide)
def slide_remove_files(instance: Slide, *args, **kwargs):
    files = instance.files
    if len(files) > 0:
        remove_files_in_bots.apply_async(kwargs={"files": files})


@receiver(post_save, sender=Channel)
def channel_active(instance: Channel, *args, **kwargs):
    print("channel_active eeee")
    if instance.previous_published == instance.published:
        return
    bot = get_bot()
    active_text = "active" if instance.published else "desactive"
    text = f"{settings.APP_ENVIRONMENT}-channel-{active_text}: {instance}"
    send_message(bot=bot, chat_id=settings.GROUP_UPLOAD_FILES, text=text)


@receiver(post_save, sender=Slide)
def slide_update_files(instance: Slide, *args, **kwargs):
    files = instance.files_changed
    if len(files) > 0:
        remove_files_in_bots.apply_async(kwargs={"files": files})


@receiver(start_conference)
def start_conference_alert_admin(conference: Conference, *args, **kwargs):
    bot = get_bot()
    text = f"{settings.APP_ENVIRONMENT}-conference-started: {conference} id: {conference.id}"
    bot.send_message(chat_id=settings.GROUP_UPLOAD_FILES, text=text)


@receiver(evaluated_conference)
def evaluated_conference_alert_admin(conference: Conference, user_conference: UserConference, *args, **kwargs):
    bot = get_bot()
    text = f"{settings.APP_ENVIRONMENT}-conference-evaluated: {conference} evaluation: {user_conference.evaluation} id: {conference.id}"
    bot.send_message(chat_id=settings.GROUP_UPLOAD_FILES, text=text)


@receiver(start_conference)
def start_conference_alert_owner(conference: Conference, user: User, *args, **kwargs):
    if not conference.alert_to_owner or conference.owner == user:
        return
    bot = get_bot()
    text = _("listener_conference_started_owner") % str(conference)
    send_message(bot=bot, chat_id=conference.owner.external_id, text=text, parse_mode=ParseMode.MARKDOWN)


@receiver(evaluated_conference)
def evaluated_conference_alert_owner(
    conference: Conference, user: User, user_conference: UserConference, *args, **kwargs
):
    if not conference.alert_to_owner or conference.owner == user:
        return
    bot = get_bot()
    text = _("listener_conference_evaluated_owner") % (str(conference), user_conference.evaluation)
    send_message(bot=bot, chat_id=conference.owner.external_id, text=text, parse_mode=ParseMode.MARKDOWN)
