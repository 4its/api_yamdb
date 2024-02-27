import csv

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from reviews.models import User, Comment, Genres, Title, Categories, Review


class Command(BaseCommand):
    help = 'Загрузить данные из CSV файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument('users_csv', type=str,
                            help='Путь к CSV файлу пользователей')
        parser.add_argument('genre_csv', type=str,
                            help='Путь к CSV файлу жанров')
        parser.add_argument('titles_csv', type=str,
                            help='Путь к CSV файлу произведений')
        parser.add_argument('genre_title_csv', type=str,
                            help='Путь к CSV файлу '
                                 'связей жанров и произведений')
        parser.add_argument('category_csv', type=str,
                            help='Путь к CSV файлу категорий')
        parser.add_argument('review_csv', type=str,
                            help='Путь к CSV файлу отзывов')
        parser.add_argument('comments_csv', type=str,
                            help='Путь к CSV файлу комментариев')

    def handle(self, *args, **options):
        user_csv = options['users_csv']
        genre_csv = options['genre_csv']
        title_csv = options['titles_csv']
        genre_title_csv = options['genre_title_csv']
        category_csv = options['category_csv']
        review_csv = options['review_csv']
        comments_csv = options['comments_csv']

        self.import_users(user_csv)
        self.import_category(category_csv)
        self.import_genre_title(genre_csv, title_csv, genre_title_csv)
        self.import_reviews(review_csv)
        self.import_comments(comments_csv)

        self.stdout.write(
            self.style.SUCCESS('Данные успешно загружены из CSV файлов'))

    def load_csv_data(self, csv_file):
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def import_genre_title(self, genre_csv, title_csv, genre_title_csv):
        genres_data = self.load_csv_data(genre_csv)
        titles_data = self.load_csv_data(title_csv)

        genres_mapping = {genre['id']: Categories.objects.get(id=genre['id'])
                          for genre in genres_data}
        titles_mapping = {title['id']: Title(**title) for title in titles_data}

        genre_title_data = self.load_csv_data(genre_title_csv)
        for item in genre_title_data:
            title_id = item['title_id']
            genre_id = item['genre_id']
            if title_id in titles_mapping:
                title_instance = titles_mapping[title_id]
                try:
                    category_instance = genres_mapping[genre_id]
                except ObjectDoesNotExist:
                    continue
                title_instance.category = category_instance
                title_instance.save()

    def import_users(self, user_csv):
        for row in csv.DictReader(open(user_csv)):
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

    def import_category(self, category_csv):
        for row in csv.DictReader(open(category_csv)):
            category = Categories(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )
            category.save()

    def import_reviews(self, review_csv):
        for row in csv.DictReader(open(review_csv)):
            review = Review(
                id=row['id'],
                title_id=row['title_id'],
                text=row['text'],
                author=row['author'],
                score=row['score'],
                pub_date=row['pub_date'],
            )
            review.save()

    def import_comments(self, comments_csv):
        for row in csv.DictReader(open(comments_csv)):
            comment = Comment(
                id=row['id'],
                review_id=row['review_id'],
                text=row['text'],
                author=row['author'],
                pub_date=row['pub_date'],
            )
            comment.save()
