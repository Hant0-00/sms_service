import requests
import random
import string
import time
from django_app.connector.models import Message

API_KEY = '4u3ox6ud488xny44toii1bgotz7ckztp'

headers = {
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}

url = 'https://restapi.easysendsms.app/v1/rest/sms/send'

# Списки вариантов для поля 'from' и 'text' (только на английском)
# from_variants = ['SolidWay',]
from_variants = [
    'TBHelper'
]

# text_variants = ['You have new message',]
text_variants = [
    'Code: {code}',
]


def send_sms(number, order):
    code = ''.join(random.choices(string.digits, k=6))

    from_choice = random.choice(from_variants)
    text_template = random.choice(text_variants)
    text_message = text_template.format(code=code)

    payload = {
        'from': from_choice,
        'to': number.number,
        'text': text_message,
        'type': '0'
    }

    Message.objects.create(
        receiver=number,
        sender=from_choice,
        text=text_message,
        order=order,
    )

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Проверка на ошибки HTTP
    except requests.exceptions.HTTPError as err:
        print(payload, err)
    time.sleep(2)