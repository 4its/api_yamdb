from django.db import models
from django.template.defaultfilters import truncatewords

WORDS_ON_TITLE = 3
WORDS_ON_TEXT = 10


class TextField(models.Model):
    def print_fields(self):
        return ' '.join([value for value in self.__dict__])


class Titles(TextField):
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выпуска')
    rating = models.IntegerField(
        default=0,
        max_length=5,
        verbose_name='Год'
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведение'
        default_related_name = 'titles'

    def __str__(self):
        return truncatewords(self.print_fields(), WORDS_ON_TEXT)
