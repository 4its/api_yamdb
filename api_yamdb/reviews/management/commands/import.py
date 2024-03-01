from collections import defaultdict
from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction

from reviews.models import Category, Comment, Genre, Review, Title, User

FILES_PATH = settings.STATIC_URL.strip('/') + '/data/'


class Counter:
    count = 0

    def add_value(self):
        self.count += 1

    def get_total(self):
        return self.count


class Command(BaseCommand):
    help = 'Импортирует записи из CSV в БД.'
    counter = Counter()

    def handle(self, *args, **options):

        IMPORT_HANDLERS = {
            self.import_user,
            self.import_category,
            self.import_genre,
            self.import_title,
            self.import_review,
            self.import_comment
        }

        for handler in IMPORT_HANDLERS:
            try:
                handler()
            except BaseException as e:
                raise ImportError(
                    f'Ошибка при импорте '
                    f'{handler.__name__}: {e}. '
                    f'Проверьте БД на конфликты и повторите попытку.'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка данных окончена, '
                f'создано строк: {self.counter.get_total()}'
            )
        )

    def import_user(self):
        with transaction.atomic():
            with open(FILES_PATH + 'users.csv') as file:
                for row in DictReader(file):
                    user = User(
                        id=row['id'],
                        username=row['username'],
                        email=row['email'],
                        role=row['role'],
                        bio=row['bio'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                    )
                    user.save()
                    self.counter.add_value()

    def import_category(self):
        with transaction.atomic():
            for row in DictReader(open(FILES_PATH + 'category.csv')):
                category = Category(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                )
                category.save()
                self.counter.add_value()

    def import_genre(self):
        with transaction.atomic():
            for row in DictReader(open(FILES_PATH + 'genre.csv')):
                genre = Genre(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                )
                genre.save()
                self.counter.add_value()

    def import_title(self):
        genre_title = defaultdict(list)
        with open(FILES_PATH + 'genre_title.csv',
                  mode='r', encoding='utf8') as file:
            for row in DictReader(file):
                genre_title[row['title_id']].append(row['genre_id'])

        with transaction.atomic():
            with open(FILES_PATH + 'titles.csv',
                      mode='r', encoding='utf8') as file:
                for row in DictReader(file):
                    title_id = row['id']

                    genres = Genre.objects.filter(id__in=genre_title[title_id])

                    title = Title(
                        id=title_id,
                        name=row['name'],
                        year=row['year'],
                        category=Category.objects.get(id=row['category']),
                    )

                    title.genre.set(genres)

                    title.save()
                    self.counter.add_value()

    def import_review(self):
        with transaction.atomic():
            with open(FILES_PATH + 'review.csv',
                      mode='r', encoding='utf8') as file:
                for row in DictReader(file):
                    review = Review(
                        id=row['id'],
                        title_id=row['title_id'],
                        text=row['text'],
                        author=User.objects.get(id=row['author']),
                        score=row['score'],
                        pub_date=row['pub_date'],
                    )
                    review.save()
                    self.counter.add_value()

    def import_comment(self):
        with transaction.atomic():
            with open(FILES_PATH + 'comments.csv',
                      mode='r', encoding='utf8') as file:
                for row in DictReader(file):
                    comment = Comment(
                        id=row['id'],
                        review_id=row['review_id'],
                        text=row['text'],
                        author=User.objects.get(id=row['author']),
                        pub_date=row['pub_date'],
                    )
                    comment.save()
                    self.counter.add_value()
