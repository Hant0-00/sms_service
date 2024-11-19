from django.utils import timezone

from django.db import models


class Message(models.Model):
    datetime_send = models.DateTimeField(auto_now_add=True)
    datetime_got = models.DateTimeField(blank=True, null=True, default=None)
    receiver = models.ForeignKey('register_service.Number', on_delete=models.DO_NOTHING)
    sender = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    order = models.ForeignKey('sender.Order', on_delete=models.DO_NOTHING, blank=True, null=True)

    def mark_as_done(self):
        self.datetime_got = timezone.now(),
        self.done = True
        self.save()
