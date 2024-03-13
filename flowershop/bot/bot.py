from django.core.management.base import BaseCommand
from django.conf import settings
import telebot
from telebot import custom_filters, callback_data
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardButton
import datetime


state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token=settings.TELEGRAM_BOT_TOKEN, state_storage=state_storage)


class BotStates(StatesGroup):
    pass


def pd_approved():
    pass


def pd_not_approved():
    pass


def get_reason():
    pass


def get_desired_sum():
    pass


def show_bouquet():
    pass


def get_client_name():
    pass


def get_client_address():
    pass


def get_client_phone_number():
    pass


def get_delivery_date():
    pass


def get_delivery_time():
    pass


def order_accepted():
    pass


def consultation_ordered():
    pass


def start(message):
    pass

if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()
