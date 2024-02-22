from datetime import datetime

from rest_framework import serializers, validators

from reviews.models import Categories, Genres, Reviews, Titles, User

USER_FIELDS_VALIDATOR = (
    validators.UniqueValidator(
        queryset=User.objects.all()
    ),
)


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации и получения confirmation_code."""

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, username):
        """Запрет использования имени 'me'."""
        if username.lower() == 'me':
            raise serializers.ValidationError("Name 'me' reserved by system")


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки запроса на получение токена с помощью
        имени пользователя и confirmation_code."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


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
            ),
        )

    def validate_username(self, username):
        """Запрет использования имени 'me'."""
        if username.lower() == 'me':
            raise serializers.ValidationError("Name 'me' reserved by system")
        return username

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class TitlesSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Categories.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genres.objects.all(),
        many=True,
        slug_field='slug'
    )

    class Meta:
        model = Titles
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )

    def validate_year(self, year):
        """Проверка года произведения"""
        if year > datetime.now().year:
            raise serializers.ValidationError(
                'the year of the work cannot be longer than the current one'
            )
        return year

    def validate_rating(self, rating):
        """Проверка рейтинга произведения"""
        max_rating = 5
        if rating > max_rating:
            raise serializers.ValidationError(
                'The rating cannot be higher than 5'
            )
        return rating

    def create(self, validated_data):
        category = validated_data.pop('category')
        if category not in Categories.objects.all():
            raise serializers.ValidationError(
                f'Category {category} does not exist'
            )
        genre_title = validated_data.pop('genre')
        all_genre = Genres.objects.all()
        if not all(genre in all_genre for genre in genre_title):
            raise serializers.ValidationError(
                f'There is no category'
            )
        title = Titles.objects.create(**validated_data, category=category)
        title.genre.set(genre_title)
        return title


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор модели Categories."""

    class Meta:
        """Метакласс сериализатора Categories."""
        exclude = ('id',)
        model = Categories


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор модели Genres."""

    class Meta:
        """Метакласс сериализатора Genres."""
        exclude = ('id',)
        model = Genres


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Reviews."""

    class Meta:
        """Метакласс сериализатора Reviews."""
        exclude = ('author', 'title',)
        model = Reviews

class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comments."""

    class Meta:
        """Метакласс сериализатора Comments."""
        model = Titles
        exclude = ('author',)
        
    def score_validate(self, validated_data):
        """Проверка оценки произведения."""
        minimum_score = 1
        maximum_score = 10

        score = validated_data.pop('score')
        if not minimum_score <= score <= maximum_score:
            raise serializers.ValidationError(
                f'Величина оценки вне диапазона '
                f'[{minimum_score}...{maximum_score}]!'
            )
        return score
