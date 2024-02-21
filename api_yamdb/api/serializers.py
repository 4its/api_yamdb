from datetime import datetime

from rest_framework import serializers

from reviews.models import Categories, Genres, Reviews, Titles


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
        fields = ('name', 'year', 'rating', 'description', 'genre', 'category')

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
        title = Titles.objects.create(**validated_data)
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
        exclude = '__all__'
        model = Reviews
