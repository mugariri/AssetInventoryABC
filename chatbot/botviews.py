import threading
from importlib import import_module

from django.conf import settings
from telebot import TeleBot

__TELEBOT_INSTANCE__ = {}

def import_name(path):
    tokens = path.split(".")
    module = import_module(".".join(tokens[:-1]))
    return getattr(module, tokens[-1])

def run_telebot():
    bot = TeleBot("5733323492:AAFj4FaXCwg2JiCiipGl_OGOPGwJaTgrljY")
    __TELEBOT_INSTANCE__['bot']=bot
    __TELEBOT_INSTANCE__['handlers']=[]
    paths = settings.TELEBOT_PARAMOUNT_HANDLERS
    for path in paths:
        __TELEBOT_INSTANCE__['handlers'].append(import_name(path))

    @bot.message_handler(func=lambda x: True)
    def receive_any_message(message):
        for handler in  __TELEBOT_INSTANCE__['handlers']:
            handler(bot, message)

    bot.infinity_polling()

def start_bot():
    thread = threading.Thread(target=run_telebot)
    thread.start()

def get_bot()->TeleBot:
    try:
        return __TELEBOT_INSTANCE__['bot']
    except KeyError:
        raise KeyError("Bot not running")



