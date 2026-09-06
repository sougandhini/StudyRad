from django.contrib import admin

# Register your models here.

from .models import Room, Topic, Message

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)

# This is to display the message admin part as 2 columns 1-msg, 2 -user 
# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ("body_preview", "user")
#     def body_preview(self, obj):
#         return obj.body[:50]
#     body_preview.short_description = "body"