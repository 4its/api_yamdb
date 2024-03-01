import csv
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.db import IntegrityError

from reviews.models import (
    Category, Comment, Genre, GenreTitle, Review, Title, User
)

FILES_PATH = os.path.join(settings.BASE_DIR, 'static/data/')

IMPORT_MODELS = {
    'category': Category,
    'genre': Genre,
    'titles': Title,
    'genre_title': GenreTitle,
    'users': User,
    'review': Review,
    'comments': Comment,
}

FIELD_MAPPING = {
    'category': ('category', Category),
    'title_id': ('title', Title),
    'genre_id': ('genre', Genre),
    'author': ('author', User),
    'review_id': ('review', Review),
}


def open_csv_file(file_name):
    """Открывает CSV файл."""
    csv_file = file_name + '.csv'
    csv_path = os.path.join(FILES_PATH, csv_file)
    try:
        with open(csv_path, encoding='utf-8') as file:
            return list(csv.reader(file))
    except FileNotFoundError:
        print(f'Файл {csv_file} не найден.')
        return None


def replace_foreign_values(data_csv):
    """Заменяет значения в CSV данных."""
    data_csv_copy = data_csv.copy()
    for field_key, field_value in data_csv.items():
        if field_key in FIELD_MAPPING:
            field_name, model_class = FIELD_MAPPING[field_key]
            data_csv_copy[field_name] = model_class.objects.get(pk=field_value)
    return data_csv_copy


def load_csv(file_name, model_class):
    """Загружает CSV файлы."""
    data = open_csv_file(file_name)
    if not data:
        return

    header, rows = data[0], data[1:]
    for row in rows:
        data_csv = dict(zip(header, row))
        data_csv = replace_foreign_values(data_csv)
        try:
            model_instance = model_class(**data_csv)
            model_instance.save()
        except (ValueError, IntegrityError) as error:
            print(f'Ошибка в загружаемых данных. {error}.')
            break


class Command(BaseCommand):
    """Команда для импорта в базу данных."""

    help = 'Импортирует записи из CSV в БД.'

    def handle(self, *args, **options):
        for file_name, model_class in IMPORT_MODELS.items():
            load_csv(file_name, model_class)

        self.stdout.write(
            self.style.SUCCESS('Данные успешно загружены!'))
