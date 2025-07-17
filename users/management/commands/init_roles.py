from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from books.models import Book, Author

class Command(BaseCommand):
    help = "Создает базовые роли: readers, librarians, moderators"

    def handle(self, *args, **options):
        # Создание групп
        readers_group, _ = Group.objects.get_or_create(name="readers")
        librarians_group, _ = Group.objects.get_or_create(name="librarians")
        moderators_group, _ = Group.objects.get_or_create(name="moderators")

        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)

        librarian_perms = Permission.objects.filter(
            content_type__in=[book_ct, author_ct],
            codename__in=[
                "view_book", "add_book", "change_book", "delete_book",
                "view_author", "add_author", "change_author", "delete_author",
            ],
        )
        librarians_group.permissions.set(librarian_perms)

        self.stdout.write(self.style.SUCCESS("Группа 'librarians' создана с правами на книги и авторов"))

        # Привязываем модераторам доступ к пользователям (если используешь кастомную модель User)
        # Можно оставить пустым — доступ у них есть по custom permission классу

        self.stdout.write(self.style.SUCCESS("Группы 'readers', 'moderators' и 'librarians' успешно созданы"))
