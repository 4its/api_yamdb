from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, SignupSerializer, TokenSerializer


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
    pass


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Category.

    Доступные HTTP методы:

    - GET;
    - POST;
    - DELETE.
    """

    pass


class GenresViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Genre.

    Доступные HTTP методы:

    - GET;
    - POST;
    - DELETE.
    """

    pass
