# Проект YaMDb
## О проекте
Проект **YaMDb** собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся (_здесь не по посмотреть фильм или послушать музыку_).  
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»). 
Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»).   
Добавлять произведения, категории и жанры может только администратор.  
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.  

Аутентифицированные пользователи могут:
* оставлять отзывы;
* ставить оценки;
* оставлять комментарии к отзывам;

### Сэк используемых технологий
 * [**Python 3.9**](https://www.python.org/downloads/release/python-390/)
 * [**Django 3.2**](https://docs.djangoproject.com/en/5.0/releases/3.2/) 
 * [**Simplejwt 5.3.1**](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html)
 * [**DRF 3.12.4**](https://www.django-rest-framework.org/community/release-notes/#3124)

  
## Ресурсы API YaMDb
* Ресурс **auth**: аутентификация.
* Ресурс **users**: пользователи.
* Ресурс **titles**: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
* Ресурс **categories**: категории (типы) произведений («Фильмы», «Книги», «Музыка»). Одно произведение может быть привязано только к одной категории.
* Ресурс **genres**: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
* Ресурс **reviews**: отзывы на произведения. Отзыв привязан к определённому произведению.
* Ресурс **comments**: комментарии к отзывам. Комментарий привязан к определённому отзыву.
Подробнее с эндпойнтами, можно ознакомится по адресу [**тут**](http://127.0.0.1/redoc/) после запуска проекта.

## Пользовательские права доступа
* **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
* **Аутентифицированный пользователь** (user) — может читать всё, как и Аноним, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по умолчанию каждому новому пользователю.
* **Модератор** (moderator) — те же права, что и у Аутентифицированного пользователя, плюс право удалять и редактировать любые отзывы и комментарии.
* **Администратор** (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.  
_**NOTE:**_ **Суперюзер Django** всегда обладает правами администратора (пользователя с правами admin). Даже если изменить пользовательскую роль суперюзера — это не лишит его прав администратора. Суперюзер — всегда администратор, но администратор — не обязательно суперюзер.

## Самостоятельная регистрация новых пользователей
1. Пользователь отправляет POST-запрос с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
2. Сервис YaMDB отправляет письмо с кодом подтверждения (`confirmation_code`) на указанный адрес email.
3. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит token (**JWT-токен**).

В результате пользователь получает токен и может работать с API проекта, отправляя этот токен с каждым запросом.   
После регистрации и получения токена пользователь может отправить `PATCH`-запрос на эндпоинт `/api/v1/users/me/` и заполнить поля в своём профайле.


## Разворачивание проекта

* Клонируем репозиторий и переходим в созданную папку:
    ```bash
    git clone https://github.com/4its/api_yamdb.git && cd api_yamdb 
    ```

* Нужно создать и активировать виртуальное окружение:
    ```bash
    python3 -m venv venv && source env/bin/activate 
    ```

* Установить зависимости из файла requirements.txt:
    ```bash
    pip install -r requirements.txt
    ```
* _При необходимости, обновите pip:_
    ```bash
    pip install --upgrade pip
    ```

*  Выполнить миграции:
    ```bash
    python3 manage.py migrate
    ```
   
* Запустить проект:
  ```bash
  python3 manage.py runserver
  ```

* **NOTE:** При желании можно импортировать тестовые данные:
    ```bash
    python3 manage.py import_csv
    ```

### Список разработчиков проекта:
* [**Nikita Goncharov**](https://github.com/ARLIKIN)
* [**Sergey Kulbida**](https://github.com/SergeyKDEV) 
* [**Goerge Egiazaryan**](https://github.com/4its)
