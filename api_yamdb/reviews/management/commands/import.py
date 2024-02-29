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

    def handle(self, *args, **options):

        counter = Counter()

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
                    counter.add_value()

        with transaction.atomic():
            for row in DictReader(open(FILES_PATH + 'category.csv')):
                category = Category(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                )
                category.save()
                counter.add_value()

        with transaction.atomic():
            for row in DictReader(open(FILES_PATH + 'genre.csv')):
                genre = Genre(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                )
                genre.save()
                counter.add_value()

        genre_title = defaultdict(list)
        with open(FILES_PATH + 'genre_title.csv',
                  mode='r', encoding='utf8') as f:
            for row in DictReader(f):
                genre_title[row['title_id']].append(row['genre_id'])

        with transaction.atomic():
            for row in DictReader(open(FILES_PATH + 'titles.csv')):
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
                counter.add_value()

        with transaction.atomic():
            for row in DictReader(open(FILES_PATH + 'review.csv')):
                review = Review(
                    id=row['id'],
                    title_id=row['title_id'],
                    text=row['text'],
                    author=User.objects.get(id=row['author']),
                    score=row['score'],
                    pub_date=row['pub_date'],
                )
                review.save()
                counter.add_value()

        with transaction.atomic():
            for row in DictReader(open(FILES_PATH + 'comments.csv')):
                comment = Comment(
                    id=row['id'],
                    review_id=row['review_id'],
                    text=row['text'],
                    author=User.objects.get(id=row['author']),
                    pub_date=row['pub_date'],
                )
                comment.save()
                counter.add_value()

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка данных окончена, '
                f'создано строк: {counter.get_total()}'
            )
        )
