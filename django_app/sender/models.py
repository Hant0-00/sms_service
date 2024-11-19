from django.db import models

from connector.models import Message


class Order(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"ID({str(self.id)}) Count:{self.count} - {self.datetime_created}"

    def get_delivery_rate(self):
        try:
            delivery_rate = str(self.get_count_of_delivery() / self.get_count_of_sent())
        except ZeroDivisionError:
            delivery_rate = "0"
        return delivery_rate + "%"

    def get_count_of_sent(self):
        return Message.objects.filter(order_id=self.id).count()

    def get_count_of_delivery(self):
        return Message.objects.filter(order_id=self.id, done=True).count()




