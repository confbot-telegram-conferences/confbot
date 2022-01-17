import emoji
import shutil
from config import celery_app
from app.conference.services.upload_zip import UploadConferenceByZip
from app.utils.telegram import get_bot, send_message, TelegramTooManyRetriesError
from app.users.models import User
from django.utils.translation import gettext_lazy as _
from celery.exceptions import SoftTimeLimitExceeded
from string import Template
from ..models import Conference


@celery_app.task(bind=True)
def upload_zip_task(self, data, user_id):
    bot = get_bot()
    user: User = User.objects.get(pk=user_id)
    try:
        uploader = UploadConferenceByZip()
        folder, slides = uploader.download_zip(bot=bot, user=user, file_data=data["file_data"])
        upload_zip_slides_task.apply_async(
            kwargs={
                "folder": folder,
                "slides": slides,
                "user_id": user_id,
                "conference_id": data["conference_id"],
                "total": len(slides),
                "start": 0,
            }
        )
    except Exception:
        text = emoji.emojize(str(_("upload_gobal_zip_error")), use_aliases=True)
        send_message(bot, chat_id=user.external_id, text=text)
        raise


@celery_app.task(bind=True, max_retries=3)
def upload_zip_slides_task(self, folder, user_id, conference_id, slides, total, start):
    bot = get_bot()
    user: User = User.objects.get(pk=user_id)
    uploader = UploadConferenceByZip()
    conference: Conference = Conference.objects.get(pk=conference_id)
    text_error = emoji.emojize(str(_("upload_global_retries_error")), use_aliases=True)
    try:
        while slides:
            start += 1
            uploader.create_slide(bot, conference, slides[0])
            text = Template(str(_("slide_upload"))).substitute(number=start, total=total)
            send_message(bot, chat_id=user.external_id, text=text)
            slides.pop(0)
        shutil.rmtree(folder)
        text = Template(str(_("conference_was_upload"))).substitute(
            name=conference.name, total=conference.slides.count(), total_processed=total
        )
        send_message(bot, chat_id=user.external_id, text=str(text))
    except (SoftTimeLimitExceeded, TelegramTooManyRetriesError) as exc:
        if self.request.retries < 2:
            send_message(bot, chat_id=user.external_id, text=str(_("upload_global_retries")))
            self.retry(
                countdown=self.request.retries * 2,
                exc=exc,
                kwargs={
                    "folder": folder,
                    "slides": slides,
                    "user_id": user_id,
                    "conference_id": conference_id,
                    "total": total,
                    "start": start,
                },
            )
        else:
            send_message(bot, chat_id=user.external_id, text=text_error)
            raise
    except Exception:
        send_message(bot, chat_id=user.external_id, text=text_error)
        raise
