from django.test import TestCase
from books.models import Author, Book, Genre
from books.serializers import AuthorSerializer, BookSerializer, GenreSerializer
from datetime import date
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TestAuthorModel(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Лев", last_name="Толстой", birthday="1828-09-09", country="Россия"
        )

    def test_str_representation(self):
        """Проверка __str__ у Author."""
        self.assertEqual(str(self.author), "Лев Толстой")


class TestGenreModel(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Роман", description="Описание жанра")

    def test_str_representation(self):
        """Проверка __str__ у Genre."""
        self.assertEqual(str(self.genre), "Роман")


class TestBookModel(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Фёдор", last_name="Достоевский", birthday="1821-11-11", country="Россия"
        )
        self.genre = Genre.objects.create(name="Классика")
        self.book = Book.objects.create(
            title="Преступление и наказание",
            author=self.author,
            published_year=1866,
            isbn="9785170905183",
            total_copies=3,
            available_copies=3,
        )
        self.book.genres.add(self.genre)

    def test_str_representation(self):
        """Проверка __str__ у Book."""
        self.assertEqual(str(self.book), "Преступление и наказание (Фёдор Достоевский)")

    def test_decrease_availability(self):
        """Проверка уменьшения доступных копий."""
        self.book.decrease_availability()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)

    def test_increase_availability(self):
        """Проверка увеличения доступных копий."""
        self.book.decrease_availability()
        self.book.increase_availability()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 3)

    def test_cannot_decrease_below_zero(self):
        """Доступные копии не могут быть меньше 0."""
        self.book.available_copies = 0
        self.book.save()
        self.book.decrease_availability()
        self.assertEqual(self.book.available_copies, 0)


class TestAuthorSerializer(TestCase):
    def test_valid_author(self):
        """Проверка успешной валидации автора."""
        data = {"first_name": "Александр", "last_name": "Пушкин", "birthday": "1799-06-06", "country": "Россия"}
        serializer = AuthorSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_author_too_young(self):
        """Автор моложе 12 лет — ошибка."""
        data = {
            "first_name": "Молодой",
            "last_name": "Автор",
            "birthday": date.today().replace(year=date.today().year - 5),  # 5 лет
            "country": "Россия",
        }
        serializer = AuthorSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Автор должен быть старше 10 лет.", str(serializer.errors))


class TestGenreSerializer(TestCase):
    def test_valid_genre(self):
        """Проверка успешной валидации жанра."""
        data = {"name": "Фантастика", "description": "Жанр фантастики"}
        serializer = GenreSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class TestBookSerializer(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Лев", last_name="Толстой", birthday="1828-09-09", country="Россия"
        )
        self.genre = Genre.objects.create(name="Роман")

    def test_valid_book(self):
        """Проверка успешной валидации книги."""
        data = {
            "title": "Война и мир",
            "author_id": self.author.id,
            "published_year": 1869,
            "isbn": "9785170905183",
            "total_copies": 5,
            "available_copies": 3,
            "genre_ids": [self.genre.id],
        }
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_available_copies_greater_than_total(self):
        """Ошибка, если available_copies > total_copies."""
        data = {
            "title": "Война и мир",
            "author_id": self.author.id,
            "published_year": 1869,
            "isbn": "9785170905183",
            "total_copies": 3,
            "available_copies": 5,  # Ошибка
            "genre_ids": [self.genre.id],
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Доступных экземпляров не может быть больше общего количества.", str(serializer.errors))

    def test_isbn_must_be_unique(self):
        """Ошибка при дублировании ISBN."""
        Book.objects.create(
            title="Анна Каренина",
            author=self.author,
            published_year=1877,
            isbn="9785170905120",
            total_copies=2,
            available_copies=2,
        )

        data = {
            "title": "Повтор",
            "author_id": self.author.id,
            "published_year": 1900,
            "isbn": "9785170905120",  # Дубликат
            "total_copies": 2,
            "available_copies": 2,
            "genre_ids": [self.genre.id],
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Книга с ISBN 9785170905120 уже существует", str(serializer.errors))


def get_token_for_user(user):
    """Возвращает access token для указанного пользователя."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class TestBookAPI(APITestCase):
    def setUp(self):
        # Создаём группы
        self.librarian_group, _ = Group.objects.get_or_create(name="librarians")
        self.reader_group, _ = Group.objects.get_or_create(name="readers")

        # Создаём пользователей
        self.librarian = User.objects.create_user(email="librarian@test.com", password="12345")
        self.reader = User.objects.create_user(email="reader@test.com", password="12345")

        # Назначаем роли
        self.librarian.groups.add(self.librarian_group)
        self.reader.groups.add(self.reader_group)

        # Создаём автора и жанр
        self.author = Author.objects.create(
            first_name="Иван", last_name="Тургенев", birthday="1818-11-09", country="Россия"
        )
        self.genre = Genre.objects.create(name="Роман")

        # Данные книги
        self.book_data = {
            "title": "Отцы и дети",
            "author_id": self.author.id,
            "published_year": 1862,
            "isbn": "9785170909999",
            "total_copies": 5,
            "available_copies": 5,
            "description": "Классический роман",
            "genre_ids": [self.genre.id],
        }

    def test_reader_cannot_create_book(self):
        """Читатель не может создавать книги."""
        token = get_token_for_user(self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/books/books/", self.book_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_create_book(self):
        """Библиотекарь может создавать книги."""
        token = get_token_for_user(self.librarian)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/books/books/", self.book_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Отцы и дети")

    def test_anyone_can_list_books(self):
        """Любой авторизованный пользователь может видеть список книг."""
        Book.objects.create(
            title="Тестовая книга",
            author=self.author,
            published_year=2000,
            isbn="9785170905188",
            total_copies=1,
            available_copies=1,
        )
        token = get_token_for_user(self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/books/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 1)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)


class TestAuthorAPI(APITestCase):
    def setUp(self):
        self.librarian_group, _ = Group.objects.get_or_create(name="librarians")
        self.reader_group, _ = Group.objects.get_or_create(name="readers")

        self.librarian = User.objects.create_user(email="lib@test.com", password="12345")
        self.reader = User.objects.create_user(email="reader2@test.com", password="12345")
        self.librarian.groups.add(self.librarian_group)
        self.reader.groups.add(self.reader_group)

        self.author_data = {
            "first_name": "Александр",
            "last_name": "Грибоедов",
            "birthday": "1795-01-04",
            "country": "Россия",
        }

    def test_reader_cannot_create_author(self):
        """Читатель не может создавать авторов."""
        token = get_token_for_user(self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/books/authors/", self.author_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_create_author(self):
        """Библиотекарь может создавать авторов."""
        token = get_token_for_user(self.librarian)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/books/authors/", self.author_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Александр")


class TestGenreAPI(APITestCase):
    def setUp(self):
        self.librarian_group, _ = Group.objects.get_or_create(name="librarians")
        self.reader_group, _ = Group.objects.get_or_create(name="readers")

        self.librarian = User.objects.create_user(email="lib2@test.com", password="12345")
        self.reader = User.objects.create_user(email="reader3@test.com", password="12345")
        self.librarian.groups.add(self.librarian_group)
        self.reader.groups.add(self.reader_group)

        self.genre_data = {"name": "Фантастика", "description": "Жанр фантастики"}

    def test_reader_cannot_create_genre(self):
        """Читатель не может создавать жанры."""
        token = get_token_for_user(self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/books/genres/", self.genre_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_create_genre(self):
        """Библиотекарь может создавать жанры."""
        token = get_token_for_user(self.librarian)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/books/genres/", self.genre_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Фантастика")


class TestBookFilterAndSearch(APITestCase):
    def setUp(self):
        # Группы
        self.librarian_group, _ = Group.objects.get_or_create(name="librarians")
        self.reader_group, _ = Group.objects.get_or_create(name="readers")

        # Пользователь-читатель
        self.reader = User.objects.create_user(email="reader_filter@test.com", password="12345")
        self.reader.groups.add(self.reader_group)

        # Автор и жанры
        self.author1 = Author.objects.create(
            first_name="Александр", last_name="Пушкин", birthday="1799-06-06", country="Россия"
        )
        self.author2 = Author.objects.create(
            first_name="Николай", last_name="Гоголь", birthday="1809-03-31", country="Россия"
        )

        self.genre1 = Genre.objects.create(name="Поэзия")
        self.genre2 = Genre.objects.create(name="Проза")

        # Книги
        self.book1 = Book.objects.create(
            title="Капитанская дочка",
            author=self.author1,
            published_year=1836,
            isbn="9785170906001",
            total_copies=2,
            available_copies=2,
        )
        self.book1.genres.add(self.genre2)

        self.book2 = Book.objects.create(
            title="Мёртвые души",
            author=self.author2,
            published_year=1842,
            isbn="9785170906002",
            total_copies=3,
            available_copies=3,
        )
        self.book2.genres.add(self.genre1)

        # Авторизация
        token = get_token_for_user(self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_filter_by_author(self):
        """Фильтр по author_id возвращает только книги нужного автора."""
        response = self.client.get(f"/api/books/books/?author={self.author1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [b["title"] for b in response.data["results"]]
        self.assertIn("Капитанская дочка", titles)
        self.assertNotIn("Мёртвые души", titles)

    def test_filter_by_genre(self):
        """Фильтр по genre_id возвращает только книги нужного жанра."""
        response = self.client.get(f"/api/books/books/?genres={self.genre1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [b["title"] for b in response.data["results"]]
        self.assertIn("Мёртвые души", titles)
        self.assertNotIn("Капитанская дочка", titles)

    def test_filter_by_published_year(self):
        """Фильтр по published_year возвращает книги за определённый год."""
        response = self.client.get("/api/books/books/?published_year=1836")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [b["title"] for b in response.data["results"]]
        self.assertIn("Капитанская дочка", titles)
        self.assertNotIn("Мёртвые души", titles)

    def test_search_by_title(self):
        """Поиск по названию книги."""
        response = self.client.get("/api/books/books/?search=Капитанская")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [b["title"] for b in response.data["results"]]
        self.assertIn("Капитанская дочка", titles)

    def test_search_by_author_last_name(self):
        """Поиск по фамилии автора."""
        response = self.client.get("/api/books/books/?search=Гоголь")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [b["title"] for b in response.data["results"]]
        self.assertIn("Мёртвые души", titles)
