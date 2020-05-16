from django.db import models

class Message(models.Model):
    timeStamp = models.DateTimeField(auto_now_add=True) 
    sender = models.CharField(max_length=1,blank=False)
    # fromTo = models.DecimalField(max_digits=1,decimal_places=0,help_text="1 => a->b || 2=> b->a")
    # read = models.DecimalField(max_digits=1,decimal_places=0,default=0,help_text="0 => unread || 1=> read")
    msg = models.TextField()
    def __str__(self):
        return f"{self.id} -> {self.timeStamp}"