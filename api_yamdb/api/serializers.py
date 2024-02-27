from datetime import datetime

from django.db.models import Avg
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from reviews.models import Categories, Genres, Review, Title, User, Comment

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
        return username


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки запроса на получение токена с помощью
        имени пользователя и confirmation_code."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=User.USERNAME_LENGTH,
    )
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    """Класс сериализатор для пользователей."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=User.USERNAME_LENGTH,
        required=True,
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

    def validate_username(self, username):
        """Запрет использования имени 'me'."""
        if username.lower() == 'me':
            raise serializers.ValidationError("Name 'me' reserved by system")
        return username

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class MeSerializer(serializers.ModelSerializer):
    """Сериализатор эндпойнта me."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        read_only_fields = ('id', 'role',)


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор модели Categories."""

    class Meta:
        """Метакласс сериализатора Categories."""
        fields = ('name', 'slug',)
        model = Categories


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор модели Genres."""

    class Meta:
        """Метакласс сериализатора Genres."""
        fields = ('name', 'slug',)
        model = Genres


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор модели Titles."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genres.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Categories.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category',)

    def get_rating(self, obj):
        num = Review.objects.filter().aggregate(avg_value=Avg('score'))
        return num['avg_value']

    def to_representation(self, instance):
        """Представление данных модели Titles при GET запросе."""
        representation = super().to_representation(instance)
        representation['genre'] = GenresSerializer(
            instance.genre, many=True).data
        representation['category'] = CategoriesSerializer(
            instance.category).data
        return representation

    def create(self, validated_data):
        """Создает экземпляр объекта Title."""
        genres_data = validated_data.pop('genre')
        category_data = validated_data.pop('category')
        title = Title.objects.create(
            category=category_data, **validated_data)
        title.genre.set(genres_data)
        title.save()
        return title

    def validate_year(self, year):
        """Проверка года произведения."""
        current_year = datetime.now().year
        if year > current_year:
            raise serializers.ValidationError(
                f'Год выпуска произведения больше {current_year}!'
            )
        return year


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Reviews."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        """Метакласс сериализатора Reviews."""
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review

    def validate(self, data):
        """Проверяет уникальность обзора."""
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')

        user = request.user

        review = Review.objects.filter(title=title_id, author=user).exists()
        if review and request.method == 'POST':
            raise ValidationError('Вы уже оставили отзыв на это произведение')

        return data

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

    def create(self, validated_data):
        score = self.score_validate(validated_data)
        return Review.objects.create(**validated_data, score=score)


class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comments."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )


    class Meta:
        """Метакласс сериализатора Comments."""
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('author', 'review',)
