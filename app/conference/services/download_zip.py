import os
import shutil
import time
import tempfile
from telegram import Bot
from slugify import slugify
from app.conference.models.conference import Conference
from app.utils.telegram import copy_file, generate_name, get_bot, send_document


class DownloadZip:
    def __call__(self, chat_id, conference_id):
        conference: Conference = Conference.objects.get(id=conference_id)
        folder = f"{tempfile.gettempdir()}/{generate_name()}"
        os.mkdir(folder)
        self._writ_conference_data(conference=conference, folder=folder)
        self._write_slides(conference=conference, folder=folder)
        zip_file = f"{tempfile.gettempdir()}/{slugify(conference.name)}-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.make_archive(zip_file, "zip", folder)
        shutil.rmtree(folder)
        bot: Bot = get_bot()
        send_document(bot, chat_id=chat_id, file_path=f"{zip_file}.zip")
        os.remove(f"{zip_file}.zip")

    def _writ_conference_data(self, conference: Conference, folder: str):
        with open(f"{folder}/data.txt", "w") as f:
            f.write(f"{conference.name}\n\n{conference.description}")

    def _write_slides(self, conference: Conference, folder: str):
        folder = f"{folder}/slides"
        os.mkdir(folder)
        for slide in conference.slides.order_by("position"):
            current_folder = f"{folder}/{slide.position}"
            os.mkdir(current_folder)
            if slide.text:
                with open(f"{current_folder}/data.txt", "w") as f:
                    f.write(f"{slide.text}")
            if slide.image:
                copy_file("image", slide.image, current_folder)
            if slide.voice:
                copy_file("audio", slide.voice, current_folder)
