from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_username, validate_year


class BaseGroup(models.Model):
    name = models.TextField(
        max_length=settings.NAME_FIELD_LENGTH,
        verbose_name='Имя'
    )
    slug = models.SlugField(
        max_length=settings.SLUG_FIELD_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        abstract = True
        ordering = ('name',)
        default_related_name = '%(class)s' + 's'

    def __str__(self):
        return self.name[:settings.OUTPUT_LENGTH]


class BasePublication(models.Model):
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)
        default_related_name = '%(class)s'+'s'

    def __str__(self):
        return self.text[:settings.OUTPUT_LENGTH]


class User(AbstractUser):
    class RoleChoice(models.TextChoices):
        user = 'user', 'Пользователь'
        moderator = 'moderator', 'Модератор'
        admin = 'admin', 'Администратор'

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.STANDARD_FIELD_LENGTH,
        unique=True,
        validators=(validate_username,)
    )
    email = models.EmailField(
        verbose_name='Эл.почта',
        max_length=settings.EMAIL_FIELD_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.STANDARD_FIELD_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.STANDARD_FIELD_LENGTH,
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
        max_length=max(len(choice) for choice in list(RoleChoice)),
    )
    confirmation_code = models.CharField(
        verbose_name='Пинкод',
        max_length=settings.PINCODE_LENGTH,
        default='None',
    )

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'пользователи'
        default_related_name = 'users'
        ordering = ('username',)

    @property
    def is_admin(self):
        return (
            self.is_superuser or self.is_staff
            or self.role == self.RoleChoice.admin
        )

    @property
    def is_moderator(self):
        return self.role == self.RoleChoice.moderator

    def __str__(self):
        return self.username[:settings.OUTPUT_LENGTH]


class Category(BaseGroup):
    """Модель для категорий."""

    class Meta(BaseGroup.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'


class Genre(BaseGroup):
    """Модель для жанра."""

    class Meta(BaseGroup.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'жанры'


class Title(models.Model):
    """Модель для произведений."""

    name = models.CharField(
        max_length=settings.NAME_FIELD_LENGTH,
        verbose_name='Название',
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=(validate_year,)
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True)
    genre = models.ManyToManyField(
        Genre
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'произведение'
        default_related_name = 'titles'
        ordering = ('year', 'name',)

    def __str__(self):
        return self.name[:settings.OUTPUT_LENGTH]


class Review(BasePublication):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Обзор',
    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(
                settings.MINIMUM_SCORE,
                f'Значение должно быть больше {settings.MINIMUM_SCORE}'
            ),
            MaxValueValidator(
                settings.MAXIMUM_SCORE,
                f'Значение должно быть меньше {settings.MAXIMUM_SCORE}'
            ),
        ),
    )

    class Meta(BasePublication.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review_for_user'
            ),
        )


class Comment(BasePublication):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
    )

    class Meta(BasePublication.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'комментарий'
