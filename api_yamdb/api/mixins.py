from reviews.validators import validate_username


class ValidateUsernameMixin:
    def validate_username(self, username):
        return username if not validate_username(username) else None
