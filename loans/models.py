from django.db import models
from django.conf import settings
from books.models import Book


class Loan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans")
    loan_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.book.title} — {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.book.available_copies == 0:
                raise ValueError("Нет доступных экземпляров книги.")
            self.book.decrease_availability()
        elif self.return_date and not Loan.objects.get(pk=self.pk).return_date:
            self.book.increase_availability()
        super().save(*args, **kwargs)
