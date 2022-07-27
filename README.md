
![example workflow](https://github.com/zhss1983/hw05_final/actions/workflows/python-app.yml/badge.svg)

# Документация к YaTube

## Описание:

YaTube - сервис публикации своего дневника. Есть полный функционал по внесению
 собственных записей с изображением и подписки на других авторов. Есть
 возможность оставлять комментарии. Классическая MVT архитектура, пагинация, 
 кэширование. Регистрация и верификация пользователей, смена пароля, 
 восстановление через почту. Тесты.

### Стек технологий:

**[Python 3](https://www.python.org/downloads/), 
[Django 3/4](https://docs.djangoproject.com/en/4.0/), 
 [MySQL](https://dev.mysql.com/doc/), 
 [Unittest](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/unit-tests/), 
 [DjangoTemplates](https://docs.djangoproject.com/en/4.0/topics/templates/), 
 HTML, 
 CSS.**

## Как работает:

Авторизация в проекте происходит за счёт стандартного модуля django.contrib.auth. Единственное изменение - я заменил
 стандартный шаблон на собственный, в едином стиле с приложением.

В проекте применяются шаблоны на базе [```DjangoTemplates```](https://docs.djangoproject.com/en/4.0/topics/templates/).
 Все страницы оформлены в едином стиле с применением
 [Bootstrap v4.3.1](https://getbootstrap.com/docs/4.3/getting-started/introduction/). Для наиболее комфортного вывода
 данных на страницу применён пагинатор, в шаблоне прописан специальный скрипт позволяющий выводить количество страниц
 доступных к просмотру. Причём лишние страницы скрываются.
 Вывод будет примерно таким: ```« Предыдущая 1 ... 4 5 6 ... 10 Следующая »```

Проект покрыт тестами. Результаты выводимые на главной странице закэшированы. 

## Как запустить проект:

Если вы собираетесь работать из командной строки в **windows**, вам может
 потребоваться Bash. скачать его можно по ссылке:
 [GitBash](https://gitforwindows.org/) ([Git-2.33.0.2-64-bit.exe](https://github.com/git-for-windows/git/releases/download/v2.33.0.windows.2/Git-2.33.0.2-64-bit.exe)).

Так же при работе в **windows** необходимо использовать **python** вместо
 **python3**

Последнюю версию **python** ищите на официальном сайте
 [https://www.python.org/](https://www.python.org/downloads/)

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/zhss1983/hw05_tests
```

```
cd hw05_tests
```

Создать и активировать виртуальное окружение:

```
python -m venv env
```

- linux
```
source env/bin/activate
```
- windows
```
source env/Scripts/activate
```

Установить зависимости из файла **requirements.txt**:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Перейти в подкаталог yatube_api и выполнить миграции:

```
cd yatube_api
python manage.py migrate
```

Создать администратора (суперпользователя) БД:

```
python manage.py createsuperuser
```

Запустить проект:

```
python manage.py runserver
```
