from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@receiver(post_save, sender=User)
def add_user_to_readers_group(sender, instance, created, **kwargs):
    """
    Автоматически добавляет нового пользователя в группу readers.
    """
    if created:
        readers_group, _ = Group.objects.get_or_create(name="readers")
        instance.groups.add(readers_group)
