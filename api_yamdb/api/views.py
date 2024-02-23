from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets, status, permissions, generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    CategoriesSerializer,
    GenresSerializer,
    ReviewsSerializer,
    TitlesSerializer,
    UserSerializer,
    MeSerializer,
    SignupSerializer,
    TokenSerializer,
)
from reviews.models import Categories, Genres, Titles, Reviews

User = get_user_model()


class UserSignupView(generics.CreateAPIView):
    """Класс для регистрации и получения confirmation_code."""

    permission_classes = (permissions.AllowAny,)

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
                [email],
                fail_silently=True,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(generics.CreateAPIView):
    """Класс для получения токена по средствам
    предоставления username и confirmation_code."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(user, confirmation_code):
            return Response(
                dict(token=str(AccessToken.for_user(user))),
                status=status.HTTP_200_OK

            )
        return Response(
            dict(confirmation_code='invalid confirmation_code'),
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями"""
    queryset = User.objects.all()
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = ('username',)
    lookup_field = 'username'
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    ordering = ('id',)


class UserMeView(generics.RetrieveAPIView):
    """Вьюсет для работы с endpoint'ом users/me."""

    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    pagination_class = PageNumberPagination
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter
    )
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')


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
    pagination_class = PageNumberPagination
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ('name',)


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
    pagination_class = PageNumberPagination
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ('name',)


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
