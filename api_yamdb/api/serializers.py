from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title, User
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
    pass


class UsersProfileSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ('id', 'role',)


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenresSerializer(many=True)
    category = CategoriesSerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )
        read_only_fields = ('__all__',)


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

    class Meta:
        model = Title
        fields = (
            'name', 'year', 'description', 'genre', 'category',
        )

    def to_representation(self, title):
        return TitleReadSerializer(title).data


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
        if request.method == 'POST':
            review = Review.objects.filter(
                title=self.context['view'].kwargs.get('title_id'),
                author=request.user
            ).exists()
            if review:
                raise ValidationError(
                    'Вы уже оставили отзыв на это произведение'
                )
        return data


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
