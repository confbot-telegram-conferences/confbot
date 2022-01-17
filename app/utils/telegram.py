import emoji
import tempfile
from time import sleep
from functools import wraps
import random
import string
from typing import Callable
import telegram
import shutil
from django.conf import settings
from telegram.error import RetryAfter, NetworkError
from telegram import Bot
from app.conference.models import Slide
from telegram.message import Message


def get_bot() -> telegram.Bot:
    return telegram.Bot(token=settings.TELEGRAM_TOKEN)


def generate_name(length=15):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def copy_file(name, src, dst):
    parts = src.split(".")
    folder_dst = f"{dst}/{name}.{parts[1]}"
    shutil.copy(src, folder_dst)
    return folder_dst


class FileBigException(BaseException):
    def __init__(self, message) -> None:
        self.message = message


class TelegramTooManyRetriesError(Exception):
    message = "Too many retries calling Telegram API."


MAX_TRIES = 3
WAIT_TIME = 15


def retry_after(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: tuple, **kwargs: dict):
        tries = 0
        wait_time = WAIT_TIME
        while tries < MAX_TRIES:
            try:
                return func(*args, **kwargs)
            except (RetryAfter, NetworkError):
                tries += 1
                wait_time += WAIT_TIME
                sleep(wait_time)
                continue

            raise

        raise TelegramTooManyRetriesError

    return wrapper


def check_file_size(max_size, file_size):
    if max_size and file_size:
        in_m = max_size / 1048576
        if file_size > max_size:
            raise FileBigException(message={"max_size": in_m})


def process_image(slide: Slide, data, type):
    bot = get_bot()
    if type == "IMAGE":
        return slide.save_image_data(data)
    file = download_file(bot, file_id=data["file_id"], path_file=tempfile.gettempdir(), ext="jpg")
    message: Message = send_photo(bot=bot, chat_id=settings.GROUP_UPLOAD_FILES, file_path=file)
    return slide.save_image_data(message.photo.pop().to_dict())


def process_audio(slide: Slide, data, type):
    bot = get_bot()
    if type == "VOICE":
        return slide.save_voice_data(data)
    file = download_file(bot, file_id=data["file_id"], path_file=tempfile.gettempdir(), ext="mp3")
    message: Message = send_voice(bot=bot, chat_id=settings.GROUP_UPLOAD_FILES, file_path=file)
    return slide.save_voice_data(message.voice.to_dict())


def download_file(bot, file_id, path_file, file_name=None, file_size=None, max_size=None, ext=None, **kwargs):
    check_file_size(max_size=max_size, file_size=file_size)
    if file_name:
        ext = file_name.split(".")[1]
    name = generate_name()
    file_name = f"{path_file}/{name}.{ext}"
    file = bot.getFile(file_id)
    file.download(file_name)
    return file_name


@retry_after
def send_photo(bot, chat_id, file_path):
    file = open(file_path, "rb")
    return bot.send_photo(chat_id=chat_id, photo=file)


@retry_after
def send_photo_by_id(bot: Bot, chat_id, file_id):
    return bot.send_photo(chat_id=chat_id, photo=file_id)


@retry_after
def send_document(bot, chat_id, file_path):
    file = open(file_path, "rb")
    return bot.send_document(chat_id=chat_id, document=file)


@retry_after
def send_voice(bot, chat_id, file_path):
    file = open(file_path, "rb")
    return bot.send_voice(chat_id=chat_id, voice=file)


@retry_after
def send_voice_by_id(bot: Bot, chat_id, file_id):
    return bot.send_voice(chat_id=chat_id, voice=file_id)


def send_message(bot, chat_id, text, **kwargs):
    text = emoji.emojize(text, use_aliases=True)
    bot.send_message(chat_id=chat_id, text=text, **kwargs)
