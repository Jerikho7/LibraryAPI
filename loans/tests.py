import unittest
from django.test import TestCase
from django.contrib.auth import get_user_model
from books.models import Book, Author, Genre
from loans.models import Loan
from datetime import date, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from loans.serializers import LoanSerializer
from rest_framework.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class TestLoanModel(TestCase):
    def setUp(self):
        # Создаём пользователя
        self.user = User.objects.create_user(email="reader@test.com", password="12345")

        # Создаём автора, жанр и книгу
        self.author = Author.objects.create(
            first_name="Александр", last_name="Пушкин", birthday="1799-06-06", country="Россия"
        )
        self.genre = Genre.objects.create(name="Поэзия")
        self.book = Book.objects.create(
            title="Капитанская дочка",
            author=self.author,
            published_year=1836,
            isbn="9785170906005",
            total_copies=3,
            available_copies=3,
        )
        self.book.genres.add(self.genre)

        # Создаём Loan
        self.loan = Loan.objects.create(user=self.user, book=self.book)

    def test_str_representation(self):
        """__str__ должен возвращать 'Название книги — email пользователя'."""
        self.assertEqual(str(self.loan), "Капитанская дочка — reader@test.com")

    def test_due_date_auto_set(self):
        """Проверка, что due_date автоматически устанавливается на +14 дней."""
        expected_due_date = self.loan.loan_date + timedelta(days=14)
        self.assertEqual(self.loan.due_date, expected_due_date)

    def test_mark_returned(self):
        """Проверка метода mark_returned (возврат книги)."""
        initial_available = self.book.available_copies
        self.loan.mark_returned()
        self.loan.refresh_from_db()
        self.book.refresh_from_db()
        self.assertIsNotNone(self.loan.return_date)
        self.assertEqual(self.book.available_copies, initial_available + 1)

    def test_renew_success(self):
        """Проверка успешного продления книги."""
        initial_due_date = self.loan.due_date
        self.loan.renew()
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.renewals_count, 1)
        self.assertEqual(self.loan.due_date, initial_due_date + timedelta(days=14))

    def test_renew_limit(self):
        """Продление книги не более 3 раз."""
        self.loan.renewals_count = 3
        self.loan.save()
        with self.assertRaises(ValueError):
            self.loan.renew()

    def test_no_available_copies(self):
        """Ошибка при создании Loan, если нет доступных копий."""
        self.book.available_copies = 0
        self.book.save()
        with self.assertRaises(ValueError):
            Loan.objects.create(user=self.user, book=self.book)

class TestLoanSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="reader_serializer@test.com", password="12345")

        self.author = Author.objects.create(
            first_name="Лев", last_name="Толстой", birthday="1828-09-09", country="Россия"
        )
        self.genre = Genre.objects.create(name="Роман")
        self.book = Book.objects.create(
            title="Война и мир",
            author=self.author,
            published_year=1869,
            isbn="9785170906006",
            total_copies=2,
            available_copies=2,
        )
        self.book.genres.add(self.genre)

    def test_valid_loan_creation(self):
        """Проверка успешного создания Loan через сериализатор."""
        data = {"user_id": self.user.id, "book_id": self.book.id}
        serializer = LoanSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        loan = serializer.save()
        self.assertEqual(loan.user, self.user)
        self.assertEqual(loan.book, self.book)
        self.assertEqual(loan.renewals_count, 0)
        self.assertEqual(loan.due_date, timezone.now().date() + timezone.timedelta(days=14))

    def test_no_available_copies(self):
        """Ошибка при создании Loan, если нет доступных копий книги."""
        self.book.available_copies = 0
        self.book.save()

        data = {"user_id": self.user.id, "book_id": self.book.id}
        serializer = LoanSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_duplicate_active_loan(self):
        """Ошибка, если у пользователя уже есть активный Loan для этой книги."""
        Loan.objects.create(user=self.user, book=self.book)

        data = {"user_id": self.user.id, "book_id": self.book.id}
        serializer = LoanSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_mark_returned_sets_return_date(self):
        """Проверка, что mark_returned устанавливает дату возврата."""
        loan = Loan.objects.create(user=self.user, book=self.book)
        self.assertIsNone(loan.return_date)
        loan.mark_returned()
        self.assertIsNotNone(loan.return_date)


def get_token_for_user(user):
    """Выдаёт JWT-токен для пользователя."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class TestLoanAPI(APITestCase):
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

        # Создаём автора, жанр и книгу
        self.author = Author.objects.create(
            first_name="Иван", last_name="Тургенев", birthday="1818-11-09", country="Россия"
        )
        self.genre = Genre.objects.create(name="Роман")
        self.book = Book.objects.create(
            title="Отцы и дети",
            author=self.author,
            published_year=1862,
            isbn="9785170909990",
            total_copies=2,
            available_copies=2,
        )
        self.book.genres.add(self.genre)

        # Токены
        self.reader_token = get_token_for_user(self.reader)
        self.librarian_token = get_token_for_user(self.librarian)

    def test_reader_cannot_create_loan(self):
        """Читатель не может создавать выдачи."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.reader_token}")
        response = self.client.post("/api/loans/", {"user_id": self.reader.id, "book_id": self.book.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_create_loan(self):
        """Библиотекарь может создать выдачу книги."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.librarian_token}")
        response = self.client.post("/api/loans/", {"user_id": self.reader.id, "book_id": self.book.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["book"]["title"], "Отцы и дети")
        self.assertEqual(response.data["user"], self.reader.email)

    def test_reader_can_view_own_loans(self):
        """Читатель видит только свои выдачи."""
        Loan.objects.create(user=self.reader, book=self.book)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.reader_token}")
        response = self.client.get("/api/loans/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for loan in response.data["results"]:
            self.assertEqual(loan["user"], self.reader.email)

    def test_librarian_can_view_all_loans(self):
        """Библиотекарь видит все выдачи."""
        Loan.objects.create(user=self.reader, book=self.book)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.librarian_token}")
        response = self.client.get("/api/loans/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_reader_can_renew_loan(self):
        """Читатель может продлить свою книгу."""
        loan = Loan.objects.create(user=self.reader, book=self.book)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.reader_token}")
        response = self.client.patch(f"/api/loans/{loan.id}/renew/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["renewals_count"], 1)

    def test_reader_cannot_renew_others_loan(self):
        """Читатель не может продлить чужую книгу."""
        other_user = User.objects.create_user(email="other@test.com", password="12345")
        loan = Loan.objects.create(user=other_user, book=self.book)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.reader_token}")
        response = self.client.patch(f"/api/loans/{loan.id}/renew/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_librarian_can_mark_return(self):
        """Библиотекарь может отметить возврат книги."""
        loan = Loan.objects.create(user=self.reader, book=self.book)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.librarian_token}")
        response = self.client.patch(f"/api/loans/{loan.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["return_date"])

    def test_reader_cannot_mark_return(self):
        """Читатель не может отметить возврат книги."""
        loan = Loan.objects.create(user=self.reader, book=self.book)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.reader_token}")
        response = self.client.patch(f"/api/loans/{loan.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
