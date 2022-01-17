from django.conf import settings
from telegram.message import Message
from app.utils.telegram import get_bot, send_photo, send_voice
from app.conference.models.slide import Slide
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Upload files to telegram"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Starting the upload the images and voices")
        count_slides = Slide.objects.count()
        self.stdout.write(f"Count of slides: {count_slides}")
        chat_id = settings.GROUP_UPLOAD_FILES
        bot = get_bot()
        images_count = 0
        voices_count = 0
        slide_counter = 0
        for slide in Slide.objects.all().iterator():
            slide_counter += 1
            if slide.image and not slide.image_id:
                message: Message = send_photo(bot=bot, chat_id=chat_id, file_path=slide.image)
                photo = message.photo
                slide.save_image_data(photo.pop().to_dict())
                images_count += 1
            if slide.voice and not slide.voice_id:
                message = send_voice(bot=bot, chat_id=chat_id, file_path=slide.voice)
                voice = message.voice
                slide.save_voice_data(voice.to_dict())
                voices_count += 1
            slide.save()
            if slide_counter % 5 == 0:
                self.stdout.write(f"Process, slides: {slide_counter}, images: {images_count}, voices: {voices_count}")
        self.stdout.write("Finished")
        self.stdout.write(f"Processed, slides: {slide_counter}, images: {images_count}, voices: {voices_count}")
