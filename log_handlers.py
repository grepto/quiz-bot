import logging
import os

import telegram
from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
TG_PROXY = os.getenv('TG_PROXY')

REQUEST_KWARGS = {
    'proxy_url': TG_PROXY,
}


def send_message(message=None):
    proxy = telegram.utils.request.Request(proxy_url=TG_PROXY)
    bot = telegram.Bot(token=TG_TOKEN, request=proxy)
    bot.send_message(chat_id=TG_CHAT_ID, text=message)


class TelegramHandler(logging.Handler):

    def emit(self, record):
        log_entry = self.format(record)
        send_message(log_entry)
