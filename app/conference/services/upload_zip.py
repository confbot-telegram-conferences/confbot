import os
import tempfile
import zipfile
import shutil
from string import Template
from os import listdir
from os.path import isfile, join, exists
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from app.utils.telegram import (
    FileBigException,
    download_file,
    generate_name,
    get_bot,
    send_message,
    send_photo,
    send_voice,
    TelegramTooManyRetriesError,
)
from app.conference.models import Slide, Conference
from app.users.models import User


class UploadError(Exception):
    def __init__(self, message) -> None:
        self.message = message


def get_position(x, prefix=""):
    try:
        x = x.lower().replace(prefix, "")
        return int(x.split(".")[0])
    except ValueError:
        return None


class UploadConferenceByZip:
    def download_zip(self, bot, file_data, user: User):
        try:
            file_path = download_file(
                bot=bot,
                file_id=file_data["file_id"],
                file_name=file_data["file_name"],
                path_file=tempfile.gettempdir(),
                file_size=file_data["file_size"],
                max_size=settings.ZIP_MAX_SIZE,
            )
            folder = f"{tempfile.gettempdir()}/{generate_name()}"
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(folder)
                folder_root = self._get_root_folder_and_validate(folder=folder)
                slides = self._get_files_slides(folder_root)
                os.remove(file_path)
                return folder_root, slides
        except FileBigException as e:
            message = _("max_size") % e.message["max_size"]
            send_message(bot, chat_id=user.external_id, text=message)
        except UploadError as e:
            send_message(bot, chat_id=user.external_id, text=e.message)
            shutil.rmtree(folder)
            os.remove(file_path)

    def _get_root_folder_and_validate(self, folder):
        check = lambda current: exists(f"{current}/slides")
        if check(folder):
            return folder
        folders = os.listdir(folder)
        if len(folders) != 1:
            raise UploadError(message=str(_("conference_structure_error")))
        folder_root = f"{folder}/{folders[0]}"
        if not check(folder_root):
            raise UploadError(message=str(_("conference_structure_error")))
        return folder_root

    def _get_file_paths(self, folder, slides, field, prefix_file=""):
        files = [f for f in listdir(folder) if isfile(join(folder, f)) and get_position(f, prefix_file)]
        for item in files:
            position = get_position(item, prefix_file)
            if position not in slides:
                slides[position] = {}
            slides[position][field] = f"{folder}/{item}"
            slides[position]["position"] = position
        return slides

    def _get_files_slides(self, folder_root):
        slides = {}
        slides = self._get_file_paths(f"{folder_root}/slides", slides, "image", "slide")
        if exists(f"{folder_root}/audios"):
            slides = self._get_file_paths(f"{folder_root}/audios", slides, "audio")
        return [slides[key] for key in sorted(slides.keys())]

    def create_slide(self, bot, conference: Conference, slide_data):
        position = slide_data["position"]
        slide: Slide = Slide.objects.get_or_create_by_position(conference=conference, position=position)
        group_chat_id = settings.GROUP_UPLOAD_FILES
        if "audio" in slide_data:
            message = send_voice(bot=bot, chat_id=group_chat_id, file_path=slide_data["audio"])
            slide.save_voice_data(message.voice.to_dict())
        if "image" in slide_data:
            message = send_photo(bot=bot, chat_id=group_chat_id, file_path=slide_data["image"])
            slide.save_image_data(message.photo.pop().to_dict())
        slide.save()


class UploadConferenceByZipV:
    def __call__(self, file_data, conference_id, user_id) -> None:
        bot = get_bot()
        user: User = User.objects.get(pk=user_id)
        try:
            file_path = download_file(
                bot=bot,
                file_id=file_data["file_id"],
                file_name=file_data["file_name"],
                path_file=tempfile.gettempdir(),
                file_size=file_data["file_size"],
                max_size=settings.ZIP_MAX_SIZE,
            )
            folder = f"{tempfile.gettempdir()}/{generate_name()}"
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(folder)
                folder_root = self._get_root_folder_and_validate(folder=folder)
                conference: Conference = Conference.objects.get(pk=conference_id)
                count_images_goog, count_images_errors = self._load_slides(
                    bot=bot, conference=conference, folder=f"{folder_root}", chat_id=user.external_id
                )
                count_audios_good, count_audios_errors = self._load_audio(
                    bot=bot, conference=conference, folder=f"{folder_root}", chat_id=user.external_id
                )
                self._send_bot_message(
                    bot=bot,
                    user=user,
                    conference=conference,
                    count_images=count_images_goog,
                    count_audios=count_audios_good,
                    count_images_errors=count_images_errors,
                    count_audios_errors=count_audios_errors,
                )
                shutil.rmtree(folder)
                os.remove(file_path)
                return {
                    "count_audios_good": count_audios_good,
                    "count_audios_errors": count_audios_errors,
                    "count_images_goog": count_images_goog,
                    "count_images_errors": count_images_errors,
                }
        except FileBigException as e:
            message = _("max_size") % e.message["max_size"]
            send_message(bot, chat_id=user.external_id, text=message)
        except UploadError as e:
            send_message(bot, chat_id=user.external_id, text=e.message)
            shutil.rmtree(folder)
            os.remove(file_path)

    def _send_bot_message(self, bot, user: User, conference: Conference, **kwargs):
        text = Template(str(_("conference_was_upload"))).substitute(name=conference.name, **kwargs)
        send_message(bot, chat_id=user.external_id, text=str(text))

    def _get_root_folder_and_validate(self, folder):
        check = lambda current: exists(f"{current}/slides")
        if check(folder):
            return folder
        folders = os.listdir(folder)
        if len(folders) != 1:
            raise UploadError(message=str(_("conference_structure_error")))
        folder_root = f"{folder}/{folders[0]}"
        if not check(folder_root):
            raise UploadError(message=str(_("conference_structure_error")))
        return folder_root

    def _process_files(
        self, bot, conference, folder, send_file, process_message, message_text, chat_id, prefix_file=""
    ):
        files = [f for f in listdir(folder) if isfile(join(folder, f)) and get_position(f, prefix_file)]
        count = 0
        good = 0
        errors = 0
        for item in sorted(files, key=lambda x: get_position(x, prefix_file)):
            position = get_position(item, prefix_file)
            slide: Slide = Slide.objects.get_or_create_by_position(conference=conference, position=position)
            group_chat_id = settings.GROUP_UPLOAD_FILES
            current_file = f"{folder}/{item}"
            try:
                message = send_file(bot=bot, chat_id=group_chat_id, file_path=current_file)
                process_message(slide, message)
                slide.save()
                good += 1
            except TelegramTooManyRetriesError:
                errors += 1
            count += 1
            text = Template(str(message_text)).substitute(number=count, total=len(files))
            send_message(bot, chat_id=chat_id, text=text)
        return good, errors

    def _load_slides(self, folder, **kwargs):
        def process_image(slide, message):
            photo = message.photo
            slide.save_image_data(photo.pop().to_dict())

        return self._process_files(
            folder=f"{folder}/slides",
            process_message=process_image,
            send_file=send_photo,
            prefix_file="slide",
            message_text=_("conference_upload_image_item"),
            **kwargs,
        )

    def _load_audio(self, folder, **kwargs):
        if not exists(f"{folder}/audios"):
            return 0, 0

        def process_audio(slide, message):
            voice = message.voice
            slide.save_voice_data(voice.to_dict())

        return self._process_files(
            folder=f"{folder}/audios",
            send_file=send_voice,
            process_message=process_audio,
            message_text=_("conference_upload_audio_item"),
            **kwargs,
        )
