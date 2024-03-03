import random

from django.conf import settings


def generate_confirmation_code(user_model, silent=True):
    confirmation_code = ''.join(random.choices(
        settings.PINCODE_CHARS,
        k=settings.PINCODE_LENGTH
    ))
    user_model.confirmation_code = confirmation_code
    user_model.save()
    if not silent:
        return confirmation_code


def check_confirmation_code(user_model, confirmation_code):
    if user_model.confirmation_code == confirmation_code:
        generate_confirmation_code(user_model, silent=True)
        return True
    else:
        generate_confirmation_code(user_model, silent=True)
        return False
