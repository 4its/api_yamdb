import re
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    if username == 'me':
        raise ValidationError(
            f'Имя пользователя "{username}" зарезервировано системой'
        )
    forbidden_chars = re.sub(settings.USERNAME_PATTERN, '', username)
    if forbidden_chars:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: "{forbidden_chars}"'
        )
    return username


def validate_year(year):
    current_year = datetime.now().year
    if year > current_year:
        raise ValidationError(
            f'Год выпуска произведения {year} не должен '
            f'превышать текущий {current_year}.'
        )
    return year
