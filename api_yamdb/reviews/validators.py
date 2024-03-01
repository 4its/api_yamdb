import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    if username.lower() in settings.RESERVED_USERNAMES:
        raise ValidationError(
            'Данное имя пользователя зарезервировано системой',
        )

    if re.search(settings.USERNAME_PATTERN, username) is None:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя {username}'
        )
