from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import (
    filters, viewsets, status, permissions, generics
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import PageNumberPagination

from .permissions import (
    AdminOrReadOnly, AdminOnly, CategoryPermission, IsAuthorOrReadOnly
)
from .filters import GenreCategoryFilter
from .serializers import (
    CategoriesSerializer, GenresSerializer, ReviewsSerializer,
    TitlesSerializer, UserSerializer, MeSerializer, SignupSerializer,
    TokenSerializer, CommentsSerializer
)
from reviews.models import User, Title, Review, Genre, Category, Comment


EXCEPTION_MESSAGES = 'Изменение чужого контента запрещено!'


class CheckAuthorMixin(viewsets.ModelViewSet):
    def perform_update(self, serializer):
        if (
                (serializer.instance.author != self.request.user)
                & (self.request.user.role not in ('admin', 'moderator'))
        ):
            raise PermissionDenied(EXCEPTION_MESSAGES)
        super(CheckAuthorMixin, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if (
                (instance.author != self.request.user)
                & (self.request.user.role not in ('admin', 'moderator'))
        ):
            raise PermissionDenied(EXCEPTION_MESSAGES)
        super(CheckAuthorMixin, self).perform_destroy(instance)


class UserSignupView(generics.CreateAPIView):
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
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = generics.get_object_or_404(User, username=username)
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
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = (AdminOnly,)
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlesSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        GenreCategoryFilter
    )
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    pagination_class = PageNumberPagination
    permission_classes = (CategoryPermission,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    pagination_class = PageNumberPagination
    permission_classes = (CategoryPermission,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ('name',)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(generics.get_object_or_404(
            Genre, slug=self.kwargs.get('pk')
        ))
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewsViewSet(CheckAuthorMixin):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorOrReadOnly,)

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

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentViewSet(CheckAuthorMixin):
    serializer_class = CommentsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
