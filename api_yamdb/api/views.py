from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets
from rest_framework.generics import get_object_or_404

from .serializers import (CategoriesSerializer,
                          GenresSerializer,
                          ReviewsSerializer,
                          TitlesSerializer)
from reviews.models import Categories, Genres, Titles, Reviews


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filterset_fields = ('name', 'year')
    search_fields = ('category__slug', 'genre__slug')


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
    ViewSet для работы с моделью Comment.

    Доступные HTTP методы:

    - GET;
    - POST;
    - DELETE.
    """

    def get_reviews(self):
        """Получает объект ревью"""
        return get_object_or_404(Reviews, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Возвращает все комментарии на ревью."""
        return self.get_reviews().comment.all()

    def perform_create(self, serializer):
        """Создает комментарий на ревью."""
        serializer.save(author=self.request.user)
