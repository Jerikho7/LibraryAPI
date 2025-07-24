from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Loan


@shared_task
def send_due_reminders():
    """Отправляет email-напоминания о скором сроке возврата книг.

    Задача выполняет следующие действия:
    1. Получает список активных выдач, срок возврата которых истекает в ближайшие 2 дня
    2. Для каждой выдачи отправляет пользователю персональное напоминание
    3. Использует стандартную систему отправки email Django

    Примечания:
    - Использует метод due_soon() менеджера Loan для получения списка выдач
    - В качестве получателя используется email пользователя из записи выдачи
    - Тема и текст письма генерируются автоматически
    - Для отправки используется DEFAULT_FROM_EMAIL из настроек Django

    Пример содержимого письма:
    Тема: Напоминание о возврате книги
    Тело:
    Здравствуйте, Иван!
    Напоминаем, что срок сдачи книги 'Python для начинающих' истекает 2023-12-31.
    Пожалуйста, верните книгу вовремя или продлите срок.
    """
    loans = Loan.objects.due_soon(days=2)

    for loan in loans:
        send_mail(
            subject="Напоминание о возврате книги",
            message=(
                f"Здравствуйте, {loan.user.first_name or loan.user.email}!\n\n"
                f"Напоминаем, что срок сдачи книги '{loan.book.title}' истекает {loan.due_date}. "
                f"Пожалуйста, верните книгу вовремя или продлите срок."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[loan.user.email],
            fail_silently=False,
        )
