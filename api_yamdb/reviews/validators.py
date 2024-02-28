import re

from django.core.exceptions import ValidationError


RESERVED_USERNAMES = ('me',)
USERNAME_PATTERN = r'^[\w.@+-]+\Z'


def validate_username(username):
    if username.lower() in RESERVED_USERNAMES:
        raise ValidationError(
            'Данное имя пользователя зарезервировано системой',
        )

    if re.search(USERNAME_PATTERN, username) is None:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя {username}'
        )
