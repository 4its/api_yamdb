from django.db import models
from django.template.defaultfilters import truncatewords

WORDS_ON_TITLE = 3
WORDS_ON_TEXT = 10


class TextField(models.Model):
    """Класс для преобразования полей модели в строку"""
    def print_fields(self):
        return ' '.join([value for value in self.__dict__])


class Titles(TextField):
    """Модель для произведений"""
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выпуска')
    rating = models.SmallIntegerField(
        default=0,
        max_length=1,
        verbose_name='Год'
    )
    description = models.TextField(verbose_name='Описание')

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
