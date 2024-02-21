from rest_framework import serializers

from reviews.models import Categories, Genres


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
