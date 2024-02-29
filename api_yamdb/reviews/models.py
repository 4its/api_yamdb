import re
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.template.defaultfilters import truncatechars, truncatewords

from .validators import validate_username


WORDS_ON_TEXT = 10      # TODO Подумать, нужно ли...
RESERVED_USERNAMES = ('me',)
STANDARD_FIELD_LENGTH = 150
NAME_FIELD_LENGTH = 256
SLUG_FIELD_LENGTH = 50
EMAIL_FIELD_LENGTH = 254
MINIMUM_SCORE = 1
MAXIMUM_SCORE = 10
OUTPUT_LENGTH = 25


class BaseCategoryGenre(models.Model):

    name = models.TextField(
        max_length=NAME_FIELD_LENGTH,
        verbose_name='Имя'
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    def __str__(self):
        return self.name[:OUTPUT_LENGTH]


class BaseReviewComment(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return self.text[:OUTPUT_LENGTH]


class User(AbstractUser):

    class RoleChoice(models.TextChoices):
        user = 'user', 'Пользователь'
        moderator = 'moderator', 'Модератор'
        admin = 'admin', 'Администратор'

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=STANDARD_FIELD_LENGTH,
        unique=True,
        validators=(validate_username,)
    )
    email = models.EmailField(
        verbose_name='Эл.почта',
        unique=True,
        max_length=EMAIL_FIELD_LENGTH,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=STANDARD_FIELD_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=STANDARD_FIELD_LENGTH,
        blank=True
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
        max_length=max(len(choice) for choice in RoleChoice.__dict__),
    )

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'пользователи'
        default_related_name = 'users'
        ordering = ('username',)

    def __str__(self):
        return self.username[:OUTPUT_LENGTH]


class Title(models.Model):
    """Модель для произведений."""

    name = models.CharField(
        max_length=NAME_FIELD_LENGTH,
        verbose_name='Название',
    )
    year = models.IntegerField(verbose_name='Год выпуска',)
    description = models.TextField(
        verbose_name='Описание',
        blank=True)
    genre = models.ManyToManyField('Genre')
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'произведение'
        default_related_name = 'titles'
        ordering = ('year', 'name')

    def clean(self):
        current_year = datetime.now().year
        if self.year > current_year:
            raise ValidationError(
                f'Год выпуска произведения не должен превышать текущий\n'
                f'{self.year} > {current_year}!'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name[:OUTPUT_LENGTH]


class Category(BaseCategoryGenre):
    """Модель для категорий."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'
        default_related_name = 'categories'
        ordering = ('name',)


class Genre(BaseCategoryGenre):
    """Модель для жанра."""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'жанры'
        default_related_name = 'genres'
        ordering = ('name',)


class Review(BaseReviewComment):

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Обзор'
    )
    score = models.SmallIntegerField(verbose_name='Оценка')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'отзывы'
        default_related_name = 'reviews'
        ordering = ('title',)
        # constraints = (
        #     models.UniqueConstraint(
        #         fields=('title', 'author'),
        #         name='unique_review'
        #     ),
        # )

    def clean(self):
        if not MINIMUM_SCORE <= self.score <= MAXIMUM_SCORE:
            raise ValidationError(
                f'Величина оценки вне диапазона '
                f'[{MINIMUM_SCORE}...{MAXIMUM_SCORE}]!'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Comment(BaseReviewComment):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'комментарий'
        default_related_name = 'comments'
        ordering = ('pub_date',)
