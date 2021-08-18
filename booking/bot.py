from .models import Reservation, Profile
from datetime import datetime


class AbstractBot():

    profile = None
    reservation = Reservation()

    def get_profile(self, user_id):
        if not isinstance(self.profile, Profile):
            self.profile = Profile.objects.get_or_create(
                external_id=user_id
            )[0]
        return self.profile

    def set_stage(self, user_id, value):
        profile = self.get_profile(user_id)
        profile.stage = value
        profile.save()
        return True

    def get_current_stage(self, user_id):
        return self.get_profile(user_id).stage

    def validate_count(self, value):
        if value.isnumeric():
            return True
        return False

    def validate_time(self, value):
        try:
            datetime.strptime(value, '%H:%M')
            return True
        except ValueError:
            return False

    def calculate_date(self, value):
        try:
            date = datetime.now().date()
            time = datetime.strptime(value, '%H:%M').time()
            return datetime.combine(date, time)
        except ValueError as e:
            raise e

    def add_reservation_attr(self, fieldname, value):
        setattr(self.reservation, fieldname, value)

    def save_reservation(self):
        self.reservation.save()
        self.reservation = Reservation()

    def do_bot(self, **kwargs):
        pass

    def __init__(self, *args, **kwargs):
        self.do_bot(**kwargs)
