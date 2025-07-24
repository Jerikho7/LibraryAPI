from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    """Кастомная команда Django для создания суперпользователя.

    Команда создает суперпользователя с предустановленными параметрами,
    если пользователь с указанным email еще не существует в базе данных.

    Attributes:
        help (str): Краткое описание команды для CLI.
    """

    help = "Создаёт суперпользователя вручную, если его ещё нет"

    def handle(self, *args, **options):
        """Основной метод выполнения команды.

        Выполняет следующие действия:
        1. Проверяет существование пользователя с email 'admin@mail.ru'
        2. Если пользователь не существует, создает суперпользователя:
           - Email: admin@mail.ru
           - Пароль: 1234qwert
           - Права: is_active, is_staff, is_superuser = True
        3. Выводит сообщение о результате выполнения

        Args:
            *args: Дополнительные позиционные аргументы.
            **options: Дополнительные именованные аргументы.

        Returns:
            None
        """
        if User.objects.filter(email="admin@mail.ru").exists():
            self.stdout.write(self.style.WARNING("Суперпользователь уже существует."))
            return

        user = User.objects.create(email="admin@mail.ru")
        user.set_password("1234qwert")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Суперпользователь {user.email} успешно создан."))
