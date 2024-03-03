import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    if username.lower() in settings.RESERVED_USERNAMES:
        raise ValidationError(
            f'Имя пользователя "{username}" зарезервировано системой',
            params={'username': username}
        )
    forbidden_chars = [char for char in set(username)
                       if (re.search(settings.USERNAME_PATTERN, char) is None)]
    if forbidden_chars:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: {forbidden_chars}'
        )
