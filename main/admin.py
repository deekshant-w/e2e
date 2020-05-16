from django.contrib import admin
from .models import Message

class adminMessage(admin.ModelAdmin):
    list_display = ("sender","timeStamp")
admin.site.register(Message,adminMessage)