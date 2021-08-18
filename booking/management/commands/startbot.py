from django.core.management.base import BaseCommand
import telebot
from telebot import types
from chatbot.settings import TELEGRAM_TOKEN
from booking.models import Profile, Reservation
import datetime


def booking():

    reservation_dict = {}

    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    print(bot.get_me())

    @bot.message_handler(content_types=['text'])
    def start(message):
        profile = Profile.objects.get_or_create(
            external_id=message.chat.id,
            defaults={
                'name': message.from_user.username
            }
        )[0]
        if message.text == '/book':
            reservation = Reservation(profile=profile)
            reservation_dict[message.chat.id] = reservation
            bot.send_message(
                message.from_user.id, "Введите количество гостей.")
            bot.register_next_step_handler(message, get_count)
        else:
            bot.send_message(
                message.from_user.id, 'Для бронирования введите /book.')

    def get_count(message):
        if message.text.isnumeric():
            reservation = reservation_dict[message.from_user.id]
            reservation.count = int(message.text)
            bot.send_message(
                message.from_user.id, 'Введите время в формате 00:00.')
            bot.register_next_step_handler(message, get_time)
        else:
            bot.send_message(
                message.from_user.id, 'Цифрами, пожалуйста.')
            bot.register_next_step_handler(message, get_count)

    def get_time(message):
        try:
            date = datetime.datetime.now().date()
            time = datetime.datetime.strptime(message.text, '%H:%M').time()
            reservation = reservation_dict[message.chat.id]
            reservation.datetime = datetime.datetime.combine(date, time)

            keyboard = types.InlineKeyboardMarkup()
            key_yes = types.InlineKeyboardButton(text='Да',
                                                 callback_data='yes')
            keyboard.add(key_yes)
            key_no = types.InlineKeyboardButton(text='Нет',
                                                callback_data='no')
            keyboard.add(key_no)
            question = 'Подтвердить бронирование?'
            bot.send_message(
                message.from_user.id, text=question, reply_markup=keyboard)
        except ValueError:
            bot.send_message(
                message.from_user.id,
                'Некорректная дата, пожалуйста, введите в формате 00:00.')
            bot.register_next_step_handler(message, get_time)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        if call.data == "yes":
            reservation = reservation_dict[call.message.chat.id]
            reservation.save()
            bot.send_message(
                call.message.chat.id,
                'Поздравляю! Место успешно забронировано!')
        elif call.data == "no":
            bot.send_message(
                call.message.chat.id, 'Будем ждать Вас в другой раз!')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Текст кнопки", reply_markup=None)

    bot.polling(none_stop=True, interval=0)


class Command(BaseCommand):
    help = 'Чат-бот'

    def handle(self, *args, **kwargs):
        return booking()
