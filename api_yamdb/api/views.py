from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets, status
from rest_framework.generics import get_object_or_404, CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (CategoriesSerializer,
                          GenresSerializer,
                          ReviewsSerializer,
                          TitlesSerializer,
                          UserSerializer,
                          SignupSerializer,
                          TokenSerializer,
                         )
from reviews.models import Categories, Genres, Titles, Reviews

User = get_user_model()


class UserSignupView(CreateAPIView):
    """Класс для регистрации и получения confirmation_code."""

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        username = request.data.get('username')
        email = request.data.get('email')
        user = User.objects.filter(username=username, email=email).exists()

        if serializer.is_valid() or user:
            user, created = User.objects.get_or_create(
                username=username,
                email=email,
            )
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                'Confirmation Code for Yamdb',
                f'Your confirmation code is: {confirmation_code}',
                'registration@yamdb.com',
                recipient_list=(email,),
                fail_silently=True,
            )

            print(f'{request.data = }')
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(CreateAPIView):
    """Класс для получения токена по средствам
    предоставления username и confirmation_code."""

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        user = get_object_or_404(User, username=request.data.get('username'))
        check_token = default_token_generator.check_token(
            user,
            request.data.get('confirmation_code')
        )
        if serializer.is_valid() and check_token:
            token = RefreshToken.for_user(user)
            return Response(
                dict(token=str(token.access_token)),
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
