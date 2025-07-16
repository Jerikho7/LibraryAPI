import unittest
from datetime import date
from books.models import Author, Book
from books.serializers import AuthorSerializer, BookSerializer


class AuthorModelTestCase(unittest.TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            birthday=date(1980, 1, 1),
            country="USA"
        )

    def test_author_str(self):
        self.assertEqual(str(self.author), "Doe John")


class BookModelTestCase(unittest.TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Jane",
            last_name="Austen",
            birthday=date(1775, 12, 16),
            country="UK"
        )
        self.book = Book.objects.create(
            title="Pride and Prejudice",
            author=self.author,
            published_year=1813,
            isbn="9781234567890",
            total_copies=5,
            available_copies=5,
            description="A classic novel"
        )

    def test_book_str(self):
        self.assertEqual(str(self.book), "Pride and Prejudice (Austen Jane)")

    def test_decrease_availability(self):
        self.book.decrease_availability()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)

    def test_increase_availability(self):
        self.book.available_copies = 3
        self.book.save()
        self.book.increase_availability()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)


class AuthorSerializerTestCase(unittest.TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Mary",
            last_name="Shelley",
            birthday=date(1797, 8, 30),
            country="UK"
        )

    def test_author_serialization(self):
        serializer = AuthorSerializer(instance=self.author)
        data = serializer.data
        self.assertEqual(data["first_name"], "Mary")
        self.assertEqual(data["last_name"], "Shelley")
        self.assertEqual(data["country"], "UK")

    def test_author_deserialization_valid(self):
        data = {
            "first_name": "Leo",
            "last_name": "Tolstoy",
            "birthday": "1828-09-09",
            "country": "Russia"
        }
        serializer = AuthorSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class BookSerializerTestCase(unittest.TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Fyodor",
            last_name="Dostoevsky",
            birthday=date(1821, 11, 11),
            country="Russia"
        )
        self.book = Book.objects.create(
            title="The Idiot",
            author=self.author,
            published_year=1869,
            isbn="9781234567897",
            total_copies=4,
            available_copies=4
        )

    def test_book_serialization(self):
        serializer = BookSerializer(instance=self.book)
        data = serializer.data
        self.assertEqual(data["title"], "The Idiot")
        self.assertEqual(data["author"]["first_name"], "Fyodor")
        self.assertEqual(data["isbn"], "9781234567897")

    def test_book_deserialization_valid(self):
        data = {
            "title": "Crime and Punishment",
            "author_id": self.author.id,
            "published_year": 1866,
            "isbn": "9781234567891",
            "total_copies": 3,
            "available_copies": 2
        }
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_isbn(self):
        data = {
            "title": "Invalid ISBN Book",
            "author_id": self.author.id,
            "published_year": 1900,
            "isbn": "123",
            "total_copies": 1,
            "available_copies": 1
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("isbn", serializer.errors)
