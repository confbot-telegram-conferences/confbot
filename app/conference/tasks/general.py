from pathlib import Path
from config import celery_app
from app.conference.services.download_zip import DownloadZip


@celery_app.task(bind=True)
def remove_files_in_bots(_, files):
    num_removed = 0
    for item in files:
        file = Path(item)
        if item and file.exists():
            file.unlink()
            num_removed += 1
    return f"{num_removed} removed"


@celery_app.task(bind=True)
def download_zip_task(_, chat_id, conference_id):
    uploader = DownloadZip()
    return uploader(chat_id=chat_id, conference_id=conference_id)


@celery_app.task(bind=True)
def sentry_check_task(self, value):
    """
    This task is for sentry testing.
    """
    a = value / 0
    return a
