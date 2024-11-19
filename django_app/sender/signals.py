import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from phone_numbers.models import Number
from .services.easysendsms import send_sms
from threading import Thread

SERVICES = {
    1: send_sms
}

logger = logging.getLogger(__name__)


def worker(numbers, service, order):
    for number in numbers:
        SERVICES[service](number, order)

def run_sending(numbers, service, order):
    Thread(target=worker, args=(numbers, service, order)).start()


@receiver(post_save, sender=Order)
def set_delivery_rate(sender, instance, created, **kwargs):
    if created:
        # Проверяем, достаточно ли номеров для назначения
        total_numbers = Number.objects.count()
        if total_numbers < instance.count:
            logger.error(f"Недостаточно номеров для назначения. Требуется: {instance.count}, доступно: {total_numbers}")
            return

        # Получаем случайные номера
        random_numbers = Number.objects.order_by('?')[:instance.count]

        # Запускаем функцию отправки сообщений
        run_sending(random_numbers, 1, instance)
