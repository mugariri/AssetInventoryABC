from telebot import TeleBot
from telebot.types import Message
from app.models import Asset, AssetCategory

from chatbot.botviews import get_bot

# def create_json(object: Asset):

def message_received(bot: TeleBot, message: Message):
    tbot = get_bot()
    tbot.reply_to(message, text=message.text)
