from django.db import models
from django.template.defaultfilters import truncatewords

WORDS_ON_TITLE = 3
WORDS_ON_TEXT = 10


class Categories:
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
        return (
            truncatewords(self.name, WORDS_ON_TEXT)
        )
