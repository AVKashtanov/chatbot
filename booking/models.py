from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя в соц. сети',
        unique=True
    )
    name = models.TextField(
        verbose_name='Имя пользователя'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'{self.external_id} | {self.name}'


class Reservation(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Профиль пользователя'
    )
    count = models.PositiveIntegerField(
        verbose_name='Количество человек'
    )
    datetime = models.DateTimeField(
        verbose_name='Дата и время'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирование'

    def __str__(self):
        return f'{self.datetime} - {self.count}'
