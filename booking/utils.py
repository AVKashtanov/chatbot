from .models import Profile
from .enums import BookingStages


# Пытаемся узнать из базы этап пользователя
def get_current_stage(user_id):
    try:
        return Profile.objects.get(external_id=user_id).stage
    except Profile.DoesNotExist:
        return BookingStages.START.value


# Сохраняем текущий этап пользователя
def set_stage(user_id, value):
    try:
        Profile.objects.update_or_create(
            external_id=user_id,
            defaults={
                'stage': value
            }
        )
        return True
    except Exception:
        return False
