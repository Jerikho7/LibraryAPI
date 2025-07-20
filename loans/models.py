from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from books.models import Book


class Loan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="loans"
    )
    loan_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    renewals_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Выдача"
        verbose_name_plural = "Выдачи"

    def __str__(self):
        return f"{self.book.title} — {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.book.available_copies == 0:
                raise ValueError("Нет доступных экземпляров книги.")

            if not self.loan_date:
                self.loan_date = timezone.now().date()

            self.book.decrease_availability()
            if not self.due_date:
                self.due_date = self.loan_date + timedelta(days=14)

        super().save(*args, **kwargs)

    def mark_returned(self):
        """Отметить книгу как возвращённую."""
        if not self.return_date:
            self.return_date = timezone.now().date()
            self.book.increase_availability()
            self.save()

    def renew(self):
        """Продлить срок возврата (максимум 3 раза)."""
        if self.renewals_count >= 3:
            raise ValueError("Продление невозможно: достигнут лимит в 3 раза.")
        self.due_date += timedelta(days=14)
        self.renewals_count += 1
        self.save()
