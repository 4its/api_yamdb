from rest_framework import serializers

from reviews.models import Categories


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор модели Categories."""

    class Meta:
        """Метакласс сериализатора Categories."""
        fields = '__all__'
        model = Categories
