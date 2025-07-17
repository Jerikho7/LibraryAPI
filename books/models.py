from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=30, help_text="Укажите имя автора", verbose_name="Имя")
    last_name = models.CharField(max_length=30, help_text="Укажите фамилию автора", verbose_name="Фамилия")
    birthday = models.DateField(
        blank=True, null=True, verbose_name="Дата рождения", help_text="Укажите дату рождения (гггг-мм-дд)"
    )
    country = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Страна", help_text="Введите страну автора"
    )

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название книги", help_text="Введите название книги")
    author = models.ForeignKey(
        "Author",
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name="Автор",
        help_text="Выберите автора книги",
    )
    published_year = models.PositiveIntegerField(verbose_name="Год издания", help_text="Укажите год издания")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN", help_text="Введите ISBN книги (13 цифр)")
    total_copies = models.PositiveIntegerField(
        default=1, verbose_name="Количество экземпляров", help_text="Общее количество экземпляров книги"
    )
    available_copies = models.PositiveIntegerField(
        default=1, verbose_name="Доступно для выдачи", help_text="Число доступных экземпляров"
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание", help_text="Опционально: краткое описание книги"
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.author})"

    def decrease_availability(self):
        """Уменьшает число доступных экземпляров на 1"""
        if self.available_copies > 0:
            self.available_copies -= 1
            self.save()

    def increase_availability(self):
        """Увеличивает число доступных экземпляров на 1"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.save()
