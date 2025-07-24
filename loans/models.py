from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from books.models import Book


class LoanQuerySet(models.QuerySet):
    """Кастомный QuerySet для модели Loan с дополнительными методами фильтрации."""

    def due_soon(self, days=2):
        """Возвращает книги, которые должны быть возвращены в ближайшие дни.

        Args:
            days (int): Количество дней для определения "ближайшего" срока (по умолчанию 2).

        Returns:
            QuerySet: Выдачи, которые должны быть возвращены в указанный период.
        """
        today = timezone.now().date()
        return self.filter(return_date__isnull=True, due_date__lte=today + timedelta(days=days), due_date__gte=today)


class LoanManager(models.Manager):
    """Кастомный менеджер для модели Loan с дополнительными методами."""

    def get_queryset(self):
        """Возвращает кастомный QuerySet для модели Loan.

        Returns:
            LoanQuerySet: Кастомный QuerySet с дополнительными методами.
        """
        return LoanQuerySet(self.model, using=self._db)

    def due_soon(self, days=2):
        """Возвращает книги, которые должны быть возвращены в ближайшие дни.

        Args:
            days (int): Количество дней для определения "ближайшего" срока.

        Returns:
            QuerySet: Выдачи, которые должны быть возвращены в указанный период.
        """
        return self.get_queryset().due_soon(days=days)


class Loan(models.Model):
    """Модель для учета выдачи книг пользователям.

    Attributes:
        user (ForeignKey): Пользователь, взявший книгу.
        book (ForeignKey): Выданная книга.
        loan_date (DateField): Дата выдачи (автоматически устанавливается при создании).
        due_date (DateField): Срок возврата.
        return_date (DateField): Фактическая дата возврата.
        renewals_count (PositiveIntegerField): Количество продлений.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans")
    loan_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    renewals_count = models.PositiveIntegerField(default=0)

    objects = LoanManager()

    class Meta:
        """Метаданные модели Loan."""

        verbose_name = "Выдача"
        verbose_name_plural = "Выдачи"
        ordering = ["-loan_date"]

    def __str__(self):
        """Строковое представление выдачи.

        Returns:
            str: Строка в формате "Название книги — email пользователя".
        """
        return f"{self.book.title} — {self.user.email}"

    def save(self, *args, **kwargs):
        """Переопределенный метод сохранения с дополнительной логикой.

        Raises:
            ValueError: Если нет доступных экземпляров книги.
        """
        if not self.pk:  # Только при создании новой записи
            if self.book.available_copies == 0:
                raise ValueError("Нет доступных экземпляров книги.")

            if not self.loan_date:
                self.loan_date = timezone.now().date()

            self.book.decrease_availability()
            if not self.due_date:
                self.due_date = self.loan_date + timedelta(days=14)

        super().save(*args, **kwargs)

    def mark_returned(self):
        """Отмечает книгу как возвращенную и увеличивает количество доступных экземпляров."""
        if not self.return_date:
            self.return_date = timezone.now().date()
            self.book.increase_availability()
            self.save()

    def renew(self):
        """Продлевает срок возврата книги.

        Raises:
            ValueError: Если достигнут лимит продлений (3 раза).
        """
        if self.renewals_count >= 3:
            raise ValueError("Продление невозможно: достигнут лимит в 3 раза.")
        self.due_date += timedelta(days=14)
        self.renewals_count += 1
        self.save()
