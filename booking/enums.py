from django.db import models
from django.utils.translation import gettext_lazy as _


class BookingStages(models.IntegerChoices):
    """Этапы бронирования"""
    START = 1, _('Выбор действия')
    COUNT = 2, _('Ввод количества гостей')
    TIME = 3, _('Ввод времени')
