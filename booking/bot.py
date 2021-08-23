from .models import Reservation, Profile
from datetime import datetime
from abc import ABC, abstractmethod
from booking.enums import BookingStages


class AbstractBot(ABC):

    social_network = None
    profile = None
    reservation = Reservation()

    @abstractmethod
    def do_bot(self, **kwargs):
        pass

    def save_profile(self, user_id):
        profile = self.get_profile(user_id)
        self._add_reservation_attr('profile', profile)

    def save_count(self, message):
        if self._validate_count(message):
            self._add_reservation_attr('count', int(message))
            return True
        else:
            return False

    def save_time(self, message):
        if self._validate_time(message):
            self._add_reservation_attr(
                'datetime', self._calculate_date(message))
            return True
        else:
            return False

    def save_reservation(self):
        self.reservation.save()
        self.reservation = Reservation()

    def get_profile(self, user_id):
        if not isinstance(self.profile, Profile):
            self.profile = Profile.objects.get_or_create(
                external_id=user_id,
                defaults={
                    'social_network': self.social_network
                }
            )[0]
        return self.profile

    def set_stage(self, user_id, value):
        profile = self.get_profile(user_id)
        profile.stage = value
        profile.save()
        return True

    def get_current_stage(self, user_id):
        return self.get_profile(user_id).stage

    def _validate_count(self, value):
        if value.isnumeric():
            return True
        return False

    def _validate_time(self, value):
        try:
            datetime.strptime(value, '%H:%M')
            return True
        except ValueError:
            return False

    def _calculate_date(self, value):
        try:
            date = datetime.now().date()
            time = datetime.strptime(value, '%H:%M').time()
            return datetime.combine(date, time)
        except ValueError as e:
            raise e

    def _add_reservation_attr(self, fieldname, value):
        setattr(self.reservation, fieldname, value)

    def __init__(self, *args, **kwargs):
        self.social_network = kwargs.get('social_network', None)
        if self.social_network:
            Profile.objects.filter(social_network=self.social_network) \
                .update(stage=BookingStages.START.value)
        self.do_bot(**kwargs)
