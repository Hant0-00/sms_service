from django.core.management import BaseCommand

from register_service.utils.service_registration import run_registration


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        while True:
            self.stdout.write("Register is running...")
            run_registration()