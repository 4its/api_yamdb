from datetime import datetime

from django.conf import settings
from django.db.models import Avg
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError

from reviews.models import (
    User, Title, Review, Genre, Category, Comment
)
from reviews.validators import validate_username


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.STANDARD_FIELD_LENGTH,
        validators=(validate_username,)
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_FIELD_LENGTH
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.STANDARD_FIELD_LENGTH,
        validators=(validate_username,)
    )
    confirmation_code = serializers.CharField()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class UserSerializer(BaseUserSerializer):
    username = serializers.CharField(
        max_length=settings.STANDARD_FIELD_LENGTH,
        validators=(validate_username,)
    )


class UsersProfileSerializer(BaseUserSerializer):

    class Meta:
        read_only_fields = ('id', 'role',)


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class TitlesSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )

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


class ReviewsSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        user = request.user
        review = Review.objects.filter(title=title_id, author=user).exists()
        if review and request.method == 'POST':
            raise ValidationError('Вы уже оставили отзыв на это произведение')
        return data


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('author', 'review',)
