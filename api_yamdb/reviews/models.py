from django.db import models
from django.template.defaultfilters import truncatewords, truncatechars
from django.contrib.auth.models import AbstractUser


WORDS_ON_TEXT = 10


class User(AbstractUser):
    """Класс для пользователя"""
    USERNAME_LENGTH = AbstractUser._meta.get_field('username').max_length
    EMAIL_FIELD_LENGTH = 254

    class RoleChoice(models.TextChoices):
        """Вспомогательный класс для определения роли пользователя."""

        user = 'user', 'User'
        moderator = 'moderator', 'Moderator'
        admin = 'admin', 'Admin'

    email = models.EmailField(
        verbose_name='Эл.почта',
        unique=True,
        max_length=EMAIL_FIELD_LENGTH,
    )

    bio = models.TextField(
        verbose_name='О себе',
        blank=True,
        null=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=RoleChoice.choices,
        default=RoleChoice.user,
        max_length=9,
    )

    class Meta:
        verbose_name = 'пользователи'
        verbose_name_plural = 'Пользователи'
        default_related_name = 'users'
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            ),
        )

    def __str__(self):
        chars_on_username = 25
        return truncatechars(self.username, chars_on_username)


class TextField(models.Model):
    """Класс для преобразования полей модели в строку"""

    def print_fields(self):
        return ' '.join([value for value in self.__dict__])


class Titles(TextField):
    """Модель для произведений"""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выпуска')
    rating = models.SmallIntegerField(
        default=0,
        verbose_name='Год'
    )
    description = models.TextField(verbose_name='Описание')
    category = models.ForeignKey(
        'Categories',
        on_delete=models.SET_NULL,
        null=True
    )
    genre = models.ManyToManyField('Genre')

    class Meta:
        """Дополнительная информация о модели Titles"""

        verbose_name = 'произведение'
        verbose_name_plural = 'Произведение'
        default_related_name = 'titles'

    def __str__(self):
        return truncatewords(self.print_fields(), WORDS_ON_TEXT)


class Categories(TextField):
    """Модель для категорий."""

    name = models.TextField(
        max_length=256,
        verbose_name='Имя категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг категории'
    )

    class Meta:
        """Дополнительная информация о модели Categories."""

        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self) -> str:
        """Возвращает все поля сообщества."""

        return truncatewords(self.print_fields(), WORDS_ON_TEXT)


class Genre(TextField):
    """Модель для жанра."""

    name = models.TextField(
        max_length=256,
        verbose_name='Имя жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг жанра'
    )

    class Meta:
        """Дополнительная информация о модели Genre."""

        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self) -> str:
        """Возвращает все поля модели Genre."""

        return truncatewords(self.print_fields(), WORDS_ON_TEXT)
