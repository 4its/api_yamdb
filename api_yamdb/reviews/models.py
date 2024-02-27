from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.template.defaultfilters import truncatechars, truncatewords


WORDS_ON_TEXT = 10


class User(AbstractUser):
    USERNAME_LENGTH = AbstractUser._meta.get_field('username').max_length
    EMAIL_FIELD_LENGTH = 254

    class RoleChoice(models.TextChoices):
        user = 'user', 'User'
        moderator = 'moderator', 'Moderator'
        admin = 'admin', 'Admin'

    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        validators=(RegexValidator(
            r'^[\w.@+-]+\Z',
            message='Имя пользователя содержит недопустимые символы'
        ),)
    )

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
        verbose_name = 'Пользователи'
        verbose_name_plural = 'пользователи'
        default_related_name = 'users'
        ordering = ('id',)

    def __str__(self):
        chars_on_username = 25
        return truncatechars(self.username, chars_on_username)


class TextField(models.Model):
    """Класс для преобразования полей модели в строку."""

    def __str__(self) -> str:
        """Возвращает все поля модели."""
        return truncatewords(
            ' '.join([value for value in self.__dict__]),
            WORDS_ON_TEXT
        )


class Title(TextField):
    """Модель для произведений."""

    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(verbose_name='Описание')
    category = models.ForeignKey(
        'Categories',
        on_delete=models.SET_NULL,
        null=True
    )
    genre = models.ManyToManyField('Genres')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'произведение'
        default_related_name = 'titles'
        ordering = ('id',)


class Categories(TextField):
    """Модель для категорий."""

    name = models.TextField(
        max_length=256,
        verbose_name='Имя'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'
        ordering = ('id',)


class Genres(TextField):
    """Модель для жанра."""

    name = models.TextField(
        max_length=256,
        verbose_name='Имя'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'жанры'


class Review(TextField):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Обзор'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.SmallIntegerField(verbose_name='(Оценка')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'отзывы'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            ),
        )


class Comment(TextField):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    reviews = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comment'
    )
    text = models.TextField(verbose_name='Текст коментария')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'комментарий'
        ordering = ('id',)
