from django.db import models

class Message(models.Model):
    timeStamp = models.DateTimeField(auto_now_add=True) 
    sender = models.CharField(max_length=1,blank=False)
    msg = models.TextField()
    def __str__(self):
        return f"{self.id} -> {self.timeStamp}"