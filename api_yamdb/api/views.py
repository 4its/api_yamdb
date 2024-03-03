from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters, generics,
    mixins, permissions,
    status, views,
    viewsets
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from reviews.utils import (
    generate_confirmation_code, check_confirmation_code
)
from .filters import GenreCategoryFilter
from .permissions import (
    AdminOnly, IsAdminOrReadOnly, IsAuthorAdminModeratorOrReadOnly,
)
from .serializers import (
    CategoriesSerializer, CommentsSerializer,
    GenresSerializer, ReviewsSerializer,
    SignupSerializer, TitleReadSerializer,
    TitlesSerializer, TokenSerializer,
    UserSerializer, UsersProfileSerializer
)


EXCEPTION_MESSAGES = 'Изменение чужого контента запрещено!'


class UserSignupView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, created = User.objects.get_or_create(
                username=username,
                email=email,
            )
        except IntegrityError:
            if User.objects.filter(username=username).exists:
                return Response(
                    dict(username=f'Имя "{username}" уже занято.'),
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                dict(email=f'Адрес "{email}" уже занят.'),
                status=status.HTTP_400_BAD_REQUEST
            )
        pincode = generate_confirmation_code(user, silent=False)
        send_mail(
            'Confirmation Code for Yamdb',
            f'Your confirmation code is: {pincode}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = generics.get_object_or_404(User, username=username)
        if check_confirmation_code(user, confirmation_code):
            return Response(
                dict(token=str(AccessToken.for_user(user))),
                status=status.HTTP_200_OK
            )
        return Response(
            dict(confirmation_code='invalid confirmation_code'),
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, AdminOnly,)
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UsersProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects
        .annotate(rating=Avg('reviews__score'))
        .order_by('year', 'name')
    )
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        GenreCategoryFilter,
    )
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitlesSerializer


class BaseGroupViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoriesViewSet(BaseGroupViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(BaseGroupViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class BasePublicationsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',)


class ReviewsViewSet(BasePublicationsViewSet):
    serializer_class = ReviewsSerializer

    def get_title(self):
        return generics.get_object_or_404(
            Title, id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(BasePublicationsViewSet):
    serializer_class = CommentsSerializer

    def get_review(self):
        return generics.get_object_or_404(
            Review, id=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review(),
        )
