from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from books.models import Book, Author, Genre

User = get_user_model()


class Command(BaseCommand):
    help = "Создает группы readers, librarians, moderators и (опционально) тестовых пользователей."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-users",
            action="store_true",
            help="Создать тестовых пользователей для каждой группы.",
        )

    def handle(self, *args, **options):
        # === Создание групп ===
        readers_group, _ = Group.objects.get_or_create(name="readers")
        librarians_group, _ = Group.objects.get_or_create(name="librarians")
        moderators_group, _ = Group.objects.get_or_create(name="moderators")

        self.stdout.write(self.style.SUCCESS("Группы созданы (или уже существовали)."))

        # === Права для библиотекаря ===
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        genre_ct = ContentType.objects.get_for_model(Genre)

        librarian_perms = Permission.objects.filter(
            content_type__in=[book_ct, author_ct, genre_ct],
            codename__in=[
                "view_book", "add_book", "change_book", "delete_book",
                "view_author", "add_author", "change_author", "delete_author",
                "view_genre", "add_genre", "change_genre", "delete_genre",
            ]
        )
        librarians_group.permissions.add(*librarian_perms)
        self.stdout.write(self.style.SUCCESS("Права для 'librarians' обновлены."))

        # === Права для модератора ===
        user_ct = ContentType.objects.get_for_model(User)
        moderator_perms = Permission.objects.filter(content_type=user_ct)
        moderators_group.permissions.add(*moderator_perms)
        self.stdout.write(self.style.SUCCESS("Права для 'moderators' обновлены."))

        # === Создание тестовых пользователей ===
        if options["with_users"]:
            self._create_test_users(readers_group, librarians_group, moderators_group)

        self.stdout.write(self.style.SUCCESS("Команда init_roles выполнена."))

    def _create_test_users(self, readers_group, librarians_group, moderators_group):
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
