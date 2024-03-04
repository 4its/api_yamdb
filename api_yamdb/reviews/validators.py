import re
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    # .lower() применено для исключения вариаций, типа: Me, mE, ME etc...
    if username.lower() in settings.RESERVED_USERNAMES:
        raise ValidationError(
            f'Имя пользователя "{username}" зарезервировано системой'
        )
    forbidden_chars = re.findall(settings.USERNAME_PATTERN, username)
    if forbidden_chars:
        raise ValidationError(
            'Недопустимые символы в'
            ' имени пользователя: {}'.format(*set(forbidden_chars))
        )


def validate_year(year):
    current_year = datetime.now().year
    if year > current_year:
        raise ValidationError(
            f'Год выпуска произведения {year} не должен '
            f'превышать текущий {current_year}.'
        )
    return year
