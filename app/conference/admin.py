from app.conference.models.channel import Channel
from app.conference.models.course import Course
from app.conference.models.category import Category
from app.conference.models.user_conference import UserConference
from app.conference.models.slide import Slide
from app.conference.models.conference import Conference
from django.contrib import admin


class SlideInlineAdmin(admin.TabularInline):
    model = Slide
    list_display = ["text", "conference"]
    ordering = ("position",)

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]
    inlines = [SlideInlineAdmin]

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(UserConference)
class UserConferenceAdmin(admin.ModelAdmin):
    list_display = ["slide_position", "conference", "user"]

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass
