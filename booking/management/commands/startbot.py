from django.core.management.base import BaseCommand
import telebot
from telebot import types
from chatbot.settings import TELEGRAM_TOKEN
from booking.enums import BookingStages
from booking.bot import AbstractBot


class TelegramBot(AbstractBot):
    def do_bot(self, **kwargs):
        bot = telebot.TeleBot(kwargs['token'])
        print(bot.get_me())

        @bot.message_handler(func=lambda message: self.get_current_stage(
            message.chat.id) == BookingStages.START.value)
        def text_start(message):
            self.save_profile(message.chat.id)
            bot.send_message(
                message.chat.id, "Для бронирования введите /start")
            self.set_stage(message.chat.id, BookingStages.COUNT.value)

        @bot.message_handler(commands=["start"])
        def cmd_start(message):
            state = self.get_current_stage(message.chat.id)
            if state == BookingStages.COUNT.value:
                bot.send_message(message.chat.id, "Введите количество гостей.")
            elif state == BookingStages.TIME.value:
                bot.send_message(
                    message.chat.id, "Введите время в формате 00:00.")
            else:
                bot.send_message(
                    message.chat.id,
                    "Привет, чтобы сделать заказ введите количество гостей!")
                self.set_stage(message.chat.id, BookingStages.COUNT.value)

        @bot.message_handler(commands=["reset"])
        def cmd_reset(message):
            self.save_profile(message.chat.id)
            bot.send_message(
                message.chat.id, "Начнем по новой, введите количество гостей.")
            self.set_stage(message.chat.id, BookingStages.COUNT.value)

        @bot.message_handler(func=lambda message: self.get_current_stage(
            message.chat.id) == BookingStages.COUNT.value)
        def get_count(message):
            if self.save_count(message.text):
                bot.send_message(
                    message.chat.id, "Введите время в формате 00:00.")
                self.set_stage(message.chat.id, BookingStages.TIME.value)
            else:
                bot.send_message(
                    message.chat.id, 'Цифрами, пожалуйста.')

        @bot.message_handler(func=lambda message: self.get_current_stage(
            message.chat.id) == BookingStages.TIME.value)
        def get_time(message):
            if self.save_time(message.text):
                keyboard = types.InlineKeyboardMarkup()
                key_yes = types.InlineKeyboardButton(text='Да',
                                                     callback_data='yes')
                keyboard.add(key_yes)
                key_no = types.InlineKeyboardButton(text='Нет',
                                                    callback_data='no')
                keyboard.add(key_no)
                question = 'Подтвердить бронирование?'
                bot.send_message(
                    message.chat.id, text=question, reply_markup=keyboard)
                self.set_stage(message.chat.id, BookingStages.START.value)
            else:
                bot.send_message(
                    message.chat.id,
                    'Некорректная дата, пожалуйста, введите в формате 00:00.')

        @bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            if call.data == "yes":
                self.save_reservation()
                bot.send_message(
                    call.message.chat.id,
                    'Место успешно забронировано!')
            elif call.data == "no":
                bot.send_message(
                    call.message.chat.id, 'Будем ждать Вас в другой раз!')
            bot.delete_message(call.message.chat.id, call.message.message_id)

        bot.polling(none_stop=True, interval=0)


class Command(BaseCommand):
    help = 'Чат-бот'

    def handle(self, *args, **kwargs):
        with TelegramBot(token=TELEGRAM_TOKEN) as bot:
            bot
