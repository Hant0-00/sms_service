import logging
import socket
import struct
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from connector.models import Message
from register_service.models import Number


logging.basicConfig(level=logging.INFO)


COMMANDS = {
    "BIND_RECEIVER": 0x00000001,
    "BIND_RECEIVER_RESP": 0x80000001,
    "BIND_TRANSMITTER": 0x00000002,
    "BIND_TRANSMITTER_RESP": 0x80000002,
    "BIND_TRANSCEIVER": 0x00000009,
    "BIND_TRANSCEIVER_RESP": 0x80000009,
    "UNBIND": 0x00000006,
    "UNBIND_RESP": 0x80000006,
    "SUBMIT_SM": 0x00000004,
    "SUBMIT_SM_RESP": 0x80000004,
    "DELIVER_SM": 0x00000005,
    "DELIVER_SM_RESP": 0x80000005,
    "ENQUIRE_LINK": 0x00000015,
    "ENQUIRE_LINK_RESP": 0x80000015,
    "GENERIC_NACK": 0x80000000,
}


class Command(BaseCommand):
    help = 'Запуск SMPP-клиента для приема сообщений'

    def handle(self, *args, **options):

        self.SMPP_SERVER_IP = getattr(settings, 'SMPP_SERVER_IP', '127.0.0.1')
        self.SMPP_SERVER_PORT = getattr(settings, 'SMPP_SERVER_PORT', 2775)
        self.SMPP_SYSTEM_ID = getattr(settings, 'SMPP_SYSTEM_ID', 'your_system_id')
        self.SMPP_PASSWORD = getattr(settings, 'SMPP_PASSWORD', 'your_password')

        while True:
            client_socket = None
            try:
                client_socket = self.connect_and_bind()
                if client_socket is None:
                    time.sleep(5)
                    continue

                while True:
                    pdu = self.receive_pdu(client_socket)
                    if pdu is None:
                        logging.error("Соединение с сервером потеряно.")
                        break

                    pdu_parsed = self.parse_pdu(pdu)
                    command_id = pdu_parsed['command_id']

                    if command_id == COMMANDS['DELIVER_SM']:
                        self.handle_deliver_sm(client_socket, pdu)
                    elif command_id == COMMANDS['ENQUIRE_LINK']:
                        self.send_enquire_link_resp(client_socket, pdu_parsed['sequence_number'])
                    else:
                        logging.warning(f"Получена неизвестная команда: {hex(command_id)}")

            except Exception as e:
                logging.exception(f"Произошла ошибка: {e}")
            finally:
                if client_socket:
                    logging.info("Закрытие соединения...")
                    client_socket.close()
                time.sleep(5)

    def create_connection(self):
        logging.info("Попытка подключения к серверу")
        logging.info(self.SMPP_SYSTEM_ID)
        logging.info(self.SMPP_PASSWORD)
        logging.info(self.SMPP_SERVER_IP)
        logging.info(self.SMPP_SERVER_PORT)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.SMPP_SERVER_IP, self.SMPP_SERVER_PORT))
        logging.info("Соединение с сервером установлено.")
        return client_socket

    def create_bind_transceiver_pdu(self, system_id, password):
        command_id = COMMANDS["BIND_TRANSCEIVER"]
        command_status = 0x00000000
        sequence_number = 1

        system_id_bytes = system_id.encode('utf-8') + b'\x00'
        password_bytes = password.encode('utf-8') + b'\x00'
        system_type_bytes = b'\x00'
        interface_version = b'\x34'
        addr_ton = b'\x00'
        addr_npi = b'\x00'
        address_range = b'\x00'

        body = (system_id_bytes + password_bytes + system_type_bytes +
                interface_version + addr_ton + addr_npi + address_range)

        command_length = 16 + len(body)
        header = struct.pack(">IIII", command_length, command_id, command_status, sequence_number)
        pdu = header + body
        return pdu

    def send_pdu(self, client_socket, pdu):
        client_socket.sendall(pdu)
        logging.debug(f"PDU отправлено на сервер({len(pdu)} байт): {pdu.hex()}")

    def receive_pdu(self, client_socket):
        header = client_socket.recv(16)
        if not header:
            return None
        command_length, = struct.unpack(">I", header[:4])
        body_length = command_length - 16
        body = client_socket.recv(body_length)
        response = header + body
        logging.debug(f"Ответ получен({len(response)} байт): {response.hex()}")
        return response

    def parse_pdu(self, pdu):
        command_length, command_id, command_status, sequence_number = struct.unpack(">IIII", pdu[:16])
        body = pdu[16:]

        return {
            'command_length': command_length,
            'command_id': command_id,
            'command_status': command_status,
            'sequence_number': sequence_number,
            'body': body
        }

    def connect_and_bind(self):
        client_socket = self.create_connection()

        bind_pdu = self.create_bind_transceiver_pdu(self.SMPP_SYSTEM_ID, self.SMPP_PASSWORD)

        self.send_pdu(client_socket, bind_pdu)

        response_pdu = self.receive_pdu(client_socket)
        if response_pdu is None:
            logging.error("Не удалось получить ответ от сервера при привязке.")
            client_socket.close()
            return None

        response = self.parse_pdu(response_pdu)
        if response['command_status'] != 0:
            logging.error(f"Ошибка при привязке: статус {response['command_status']}")
            client_socket.close()
            return None

        logging.info("Привязка к серверу успешно выполнена.")
        return client_socket

    def read_cstring(self, data, offset):
        end = data.find(b'\x00', offset)
        if end == -1:
            raise ValueError("Нулевой байт не найден при чтении C-строки.")
        value = data[offset:end].decode('utf-8')
        offset = end + 1
        return value, offset

    def handle_deliver_sm(self, client_socket, pdu):
        pdu_parsed = self.parse_pdu(pdu)
        body = pdu_parsed['body']

        offset = 0
        try:
            service_type, offset = self.read_cstring(body, offset)
            source_addr_ton = body[offset]
            offset += 1
            source_addr_npi = body[offset]
            offset += 1
            source_addr, offset = self.read_cstring(body, offset)
            dest_addr_ton = body[offset]
            offset += 1
            dest_addr_npi = body[offset]
            offset += 1
            destination_addr, offset = self.read_cstring(body, offset)
            esm_class = body[offset]
            offset += 1
            protocol_id = body[offset]
            offset += 1
            priority_flag = body[offset]
            offset += 1
            schedule_delivery_time, offset = self.read_cstring(body, offset)
            validity_period, offset = self.read_cstring(body, offset)
            registered_delivery = body[offset]
            offset += 1
            replace_if_present_flag = body[offset]
            offset += 1
            data_coding = body[offset]
            offset += 1
            sm_default_msg_id = body[offset]
            offset += 1
            sm_length = body[offset]
            offset += 1
            short_message = body[offset:offset+sm_length]
            offset += sm_length

            if data_coding == 0:  # SMSC Default Alphabet (GSM 7-bit)
                message_text = short_message.decode('utf-8', errors='replace')
            elif data_coding == 8:  # UCS2 encoding
                message_text = short_message.decode('utf-16-be', errors='replace')
            else:
                message_text = short_message.decode('utf-8', errors='replace')

            logging.info("-"*100)
            logging.info("Получено входящее сообщение deliver_sm.")
            logging.info(f"Отправитель: {source_addr}")
            logging.info(f"Получатель: {destination_addr}")
            logging.info(f"Текст сообщения: {message_text}")

            self.process_incoming_message(source_addr, destination_addr, message_text)

        except Exception as e:
            logging.exception(f"Ошибка при разборе deliver_sm: {e}")

        self.send_deliver_sm_resp(client_socket, pdu_parsed['sequence_number'])

    def send_deliver_sm_resp(self, client_socket, sequence_number):
        command_id = COMMANDS['DELIVER_SM_RESP']
        command_status = 0x00000000
        command_length = 16
        pdu = struct.pack(">IIII", command_length, command_id, command_status, sequence_number)
        self.send_pdu(client_socket, pdu)
        logging.debug("Отправлено deliver_sm_resp.")

    def send_enquire_link_resp(self, client_socket, sequence_number):
        command_id = COMMANDS['ENQUIRE_LINK_RESP']
        command_status = 0x00000000
        command_length = 16
        pdu = struct.pack(">IIII", command_length, command_id, command_status, sequence_number)
        self.send_pdu(client_socket, pdu)
        logging.debug("Отправлено enquire_link_resp.")

    def process_incoming_message(self, source_addr, destination_addr, message_text):
        """
        Обрабатывает входящее сообщение и сохраняет его в базе данных.

        :param source_addr: Номер отправителя (строка)
        :param destination_addr: Номер получателя (строка)
        :param message_text: Текст сообщения (строка)
        """
        try:
            receiver, _ = Number.objects.get_or_create(number=destination_addr)
            logging.debug(destination_addr)
            logging.debug(receiver)
        except Number.DoesNotExist:
            logging.warning(f"Отправитель с номером {destination_addr} не найден в модели Number.")
            return
            # Пример создания записи Number:
            # sender = Number.objects.create(number=source_addr)

        try:
            message = Message.objects.get(sender=source_addr, receiver=receiver, text=message_text)
            message.mark_as_done()
            logging.info(f"Сообщение обновлено: от {source_addr} к {destination_addr}.")
        except Message.DoesNotExist:
            Message.objects.create(
                sender=source_addr,
                receiver=receiver,
                text=message_text,
                datetime_got=timezone.now(),
                done=True
            )
            logging.info(f"Новое сообщение создано: от {source_addr} к {destination_addr}.")