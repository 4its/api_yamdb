from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import truncatechars, truncatewords


WORDS_ON_TEXT = 10


class User(AbstractUser):
    """Класс для пользователя."""

    class RoleChoice(models.TextChoices):
        """Вспомогательный класс для определения роли пользователя."""

        user = 'user', 'User'
        moderator = 'moderator', 'Moderator'
        admin = 'admin', 'Admin'

    email = models.EmailField(
        verbose_name='Эл.почта',
        unique=True,
        max_length=254,
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
        """Дополнительная информация и ограничения для модели Role."""
        verbose_name = 'Пользователи'
        verbose_name_plural = 'пользователи'
        default_related_name = 'users'
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            ),
        )

    def __str__(self):
        """Возвращает имя пользователя."""
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


class Titles(TextField):
    """Модель для произведений."""

    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выпуска')
    rating = models.SmallIntegerField(
        default=0,
        verbose_name='Рейтинг'
    )
    description = models.TextField(verbose_name='Описание')
    category = models.ForeignKey(
        'Categories',
        on_delete=models.SET_NULL,
        null=True
    )
    genre = models.ManyToManyField('Genre')

    class Meta:
        """Дополнительная информация о модели Titles."""
        verbose_name = 'Произведение'
        verbose_name_plural = 'произведение'
        default_related_name = 'titles'


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
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'


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
        verbose_name = 'Жанр'
        verbose_name_plural = 'жанры'


class Reviews(TextField):
    """Модель для отзывов."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.SmallIntegerField(verbose_name='(Оценка')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        """Дополнительная информация о модели Reviews."""
        verbose_name = 'Отзыв'
        verbose_name_plural = 'отзывы'


class Comment(TextField):
    """Модель для комментариев."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        related_name='comment'
    )
    text = models.TextField(verbose_name='Текст коментария')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        """Дополнительная информация о модели Comment."""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'комментарий'
