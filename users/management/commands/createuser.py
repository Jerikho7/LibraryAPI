from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создаёт суперпользователя вручную, если его ещё нет"

    def handle(self, *args, **options):
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
