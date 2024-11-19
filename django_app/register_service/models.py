from django.db import models


class Number(models.Model):
    number = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return self.number