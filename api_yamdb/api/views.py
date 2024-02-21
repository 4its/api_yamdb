from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from .serializers import (CategoriesSerializer,
                          GenresSerializer,
                          ReviewsSerializer)
from reviews.models import Categories, Genres, Reviews, Titles


class TitleViewSet(viewsets.ModelViewSet):
    pass


class CategoriesViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Category.

    Доступные HTTP методы:

    - GET;
    - POST;
    - DELETE.
    """

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Genre.

    Доступные HTTP методы:

    - GET;
    - POST;
    - DELETE.
    """

    queryset = Genres.objects.all()
    serializer_class = GenresSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Genre.

    Доступные HTTP методы:

    - GET;
    - POST;
    - DELETE.
    """

    serializer_class = ReviewsSerializer

    def get_title(self):
        """Получает объект произведения."""
        return get_object_or_404(Titles, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает все обзоры на произведение."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создает обзор на произведение."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Genre.

    Доступные HTTP методы:

    - GET;
    - POST;
    - DELETE.
    """

    pass
