from rest_framework import serializers

from reviews.models import Categories, Genres, Reviews


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
