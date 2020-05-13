from django.contrib import admin
from .models import Message

class adminMessage(admin.ModelAdmin):
    list_display = ("fromTo","read","timeStamp")
    def fromTo(self, obj):
        print(self.fromTo)
        return self.fromTo + 1
admin.site.register(Message,adminMessage)