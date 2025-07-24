from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from books.models import Book, Author, Genre

User = get_user_model()


class Command(BaseCommand):
    """Кастомная команда Django для инициализации ролей и пользователей.

    Создает три группы пользователей с разными правами:
    - readers: базовые права на просмотр
    - librarians: полные права на управление книгами, авторами и жанрами
    - moderators: права на управление пользователями

    Дополнительно может создавать тестовых пользователей для каждой группы.
    """

    help = "Создает группы readers, librarians, moderators и (опционально) тестовых пользователей."

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки.

        Args:
            parser (ArgumentParser): Парсер аргументов командной строки.
        """
        parser.add_argument(
            "--with-users",
            action="store_true",
            help="Создать тестовых пользователей для каждой группы.",
        )

    def handle(self, *args, **options):
        """Основной метод выполнения команды.

        Выполняет:
        1. Создание групп пользователей
        2. Назначение прав для библиотекарей и модераторов
        3. Опциональное создание тестовых пользователей

        Args:
            *args: Дополнительные позиционные аргументы.
            **options: Аргументы командной строки.
        """
        # Создание групп
        readers_group, _ = Group.objects.get_or_create(name="readers")
        librarians_group, _ = Group.objects.get_or_create(name="librarians")
        moderators_group, _ = Group.objects.get_or_create(name="moderators")

        self.stdout.write(self.style.SUCCESS("Группы созданы (или уже существовали)."))

        # Назначение прав библиотекарям
        self._setup_librarian_permissions(librarians_group)
        # Назначение прав модераторам
        self._setup_moderator_permissions(moderators_group)

        # Создание тестовых пользователей
        if options["with_users"]:
            self._create_test_users(readers_group, librarians_group, moderators_group)

        self.stdout.write(self.style.SUCCESS("Команда init_roles выполнена."))

    def _setup_librarian_permissions(self, group):
        """Настраивает права доступа для группы библиотекарей.

        Включает полные CRUD-права для:
        - Книг (Book)
        - Авторов (Author)
        - Жанров (Genre)

        Args:
            group (Group): Группа библиотекарей.
        """
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        genre_ct = ContentType.objects.get_for_model(Genre)

        librarian_perms = Permission.objects.filter(
            content_type__in=[book_ct, author_ct, genre_ct],
            codename__in=[
                "view_book",
                "add_book",
                "change_book",
                "delete_book",
                "view_author",
                "add_author",
                "change_author",
                "delete_author",
                "view_genre",
                "add_genre",
                "change_genre",
                "delete_genre",
            ],
        )
        group.permissions.add(*librarian_perms)
        self.stdout.write(self.style.SUCCESS("Права для 'librarians' обновлены."))

    def _setup_moderator_permissions(self, group):
        """Настраивает права доступа для группы модераторов.

        Включает полные права на управление пользователями (User).

        Args:
            group (Group): Группа модераторов.
        """
        user_ct = ContentType.objects.get_for_model(User)
        moderator_perms = Permission.objects.filter(content_type=user_ct)
        group.permissions.add(*moderator_perms)
        self.stdout.write(self.style.SUCCESS("Права для 'moderators' обновлены."))

    def _create_test_users(self, readers_group, librarians_group, moderators_group):
        """Создает тестовых пользователей для каждой группы.

        Args:
            readers_group (Group): Группа читателей.
            librarians_group (Group): Группа библиотекарей.
            moderators_group (Group): Группа модераторов.
        """
        test_users = [
            ("reader@example.com", "reader123", readers_group),
            ("librarian@example.com", "librarian123", librarians_group),
            ("moderator@example.com", "moderator123", moderators_group),
        ]

        for email, password, group in test_users:
            user, created = User.objects.get_or_create(email=email)
            if created:
                user.set_password(password)
                user.username = email
                user.save()
                user.groups.add(group)
                self.stdout.write(self.style.SUCCESS(f"Создан пользователь {email}"))
            else:
                self.stdout.write(f"Пользователь {email} уже существует.")
