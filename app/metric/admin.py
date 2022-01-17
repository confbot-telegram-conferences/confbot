from app.metric.models.group_channel import GroupChannel
from django.contrib import admin


@admin.register(GroupChannel)
class GroupChannelAdmin(admin.ModelAdmin):
    pass
