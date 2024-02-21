from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework import filters

from reviews.models import Titles

from .serializers import TitlesSerializer

from .serializers import CategoriesSerializer, GenresSerializer
from reviews.models import Categories, Genres


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

    pass


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Genre.

    Доступные HTTP методы:

    - GET;
    - POST;
    - DELETE.
    """

    pass
