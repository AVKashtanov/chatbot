from django.core.management.base import BaseCommand
import telebot
from telebot import types
from chatbot.settings import TELEGRAM_TOKEN
from booking.models import Profile, Reservation
import datetime
from booking.utils import get_current_state, set_state
from booking.enums import BookingStages


def booking():

    reservation_dict = {}

    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    print(bot.get_me())

    @bot.message_handler(func=lambda message: get_current_state(
        message.chat.id) == BookingStages.START.value)
    def text_start(message):
        bot.send_message(message.chat.id, "Для бронирования введите /start")
        set_state(message.chat.id, BookingStages.COUNT.value)

    @bot.message_handler(commands=["start"])
    def cmd_start(message):
        profile = Profile.objects.get_or_create(
            external_id=message.chat.id,
            defaults={
                'name': message.from_user.username
            }
        )[0]
        reservation = Reservation(profile=profile)
        reservation_dict[message.chat.id] = reservation
        state = get_current_state(message.chat.id)
        if state == BookingStages.COUNT.value:
            bot.send_message(message.chat.id, "Введите количество гостей.")
        elif state == BookingStages.TIME.value:
            bot.send_message(message.chat.id, "Введите время в формате 00:00.")
        else:
            bot.send_message(
                message.chat.id,
                "Привет, чтобы сделать заказ введите количество гостей!")
            set_state(message.chat.id, BookingStages.COUNT.value)

    @bot.message_handler(commands=["reset"])
    def cmd_reset(message):
        bot.send_message(
            message.chat.id, "Начнем по новой, введите количество гостей.")
        set_state(message.chat.id, BookingStages.COUNT.value)

    @bot.message_handler(func=lambda message: get_current_state(
        message.chat.id) == BookingStages.COUNT.value)
    def get_count(message):
        if message.text.isnumeric():
            reservation = reservation_dict[message.chat.id]
            reservation.count = int(message.text)
            bot.send_message(message.chat.id, "Введите время в формате 00:00.")
            set_state(message.chat.id, BookingStages.TIME.value)
        else:
            bot.send_message(
                message.chat.id, 'Цифрами, пожалуйста.')

    @bot.message_handler(func=lambda message: get_current_state(
        message.chat.id) == BookingStages.TIME.value)
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
                message.chat.id, text=question, reply_markup=keyboard)
            set_state(message.chat.id, BookingStages.START.value)
        except ValueError:
            bot.send_message(
                message.chat.id,
                'Некорректная дата, пожалуйста, введите в формате 00:00.')

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        if call.data == "yes":
            reservation = reservation_dict[call.message.chat.id]
            reservation.save()
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
        return booking()
