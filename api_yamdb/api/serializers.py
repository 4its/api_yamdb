from rest_framework import serializers, validators
from reviews.models import Titles, Categories, User

USER_FIELDS_VALIDATOR = (
    validators.UniqueValidator(
        queryset=User.objects.all()
    ),
)


class UserSerializer(serializers.ModelSerializer):
    """Класс сериализатор для пользователей."""

    username = serializers.CharField(
        required=True,
        max_length=User.USERNAME_LENGTH,
        validators=USER_FIELDS_VALIDATOR
    )
    email = serializers.EmailField(
        required=True,
        max_length=User.EMAIL_FIELD_LENGTH,
        validators=USER_FIELDS_VALIDATOR
        )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email'),
                message='User already exists',
            )
        )

    def validate_username(self, username):
        """Запрет использования имени 'me'."""
        if username.lower() == 'me':
            raise serializers.ValidationError("Name 'me' reserved by system")
        return username
