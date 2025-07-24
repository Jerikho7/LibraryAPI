from django.db import models


class Author(models.Model):
    """Модель автора книги.

    Attributes:
        first_name (CharField): Имя автора.
        last_name (CharField): Фамилия автора.
        birthday (DateField): Дата рождения (необязательное поле).
        country (CharField): Страна автора (необязательное поле).
    """

    first_name = models.CharField(max_length=30, help_text="Укажите имя автора", verbose_name="Имя")
    last_name = models.CharField(max_length=30, help_text="Укажите фамилию автора", verbose_name="Фамилия")
    birthday = models.DateField(
        blank=True, null=True, verbose_name="Дата рождения", help_text="Укажите дату рождения (гггг-мм-дд)"
    )
    country = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Страна", help_text="Введите страну автора"
    )

    class Meta:
        """Метаданные модели Author."""

        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "birthday"],
                name="unique_author",
                violation_error_message="Автор с такими данными уже существует.",
            )
        ]

    def __str__(self):
        """Строковое представление автора (фамилия + имя)."""
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    """Модель жанра книги.

    Attributes:
        name (CharField): Название жанра (уникальное).
        description (TextField): Описание жанра (необязательное).
    """

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        """Метаданные модели Genre."""

        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        """Строковое представление жанра (название)."""
        return self.name


class Book(models.Model):
    """Модель книги.

    Attributes:
        title (CharField): Название книги.
        author (ForeignKey): Автор книги.
        published_year (PositiveIntegerField): Год издания.
        isbn (CharField): Уникальный ISBN (13 цифр).
        total_copies (PositiveIntegerField): Общее количество экземпляров.
        available_copies (PositiveIntegerField): Доступные для выдачи экземпляры.
        description (TextField): Описание книги (необязательное).
        genres (ManyToManyField): Связанные жанры.
    """

    title = models.CharField(max_length=255, verbose_name="Название книги", help_text="Введите название книги")
    author = models.ForeignKey(
        "Author",
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name="Автор",
        help_text="Выберите автора книги",
    )
    published_year = models.PositiveIntegerField(verbose_name="Год издания", help_text="Укажите год издания")
    isbn = models.CharField(
        max_length=13,
        unique=True,
        verbose_name="ISBN",
        help_text="Введите ISBN книги (13 цифр)",
        error_messages={"unique": "Книга с таким ISBN уже существует. Проверьте корректность или измените данные."},
    )
    total_copies = models.PositiveIntegerField(
        default=1, verbose_name="Количество экземпляров", help_text="Общее количество экземпляров книги"
    )
    available_copies = models.PositiveIntegerField(
        default=1, verbose_name="Доступно для выдачи", help_text="Число доступных экземпляров"
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание", help_text="Опционально: краткое описание книги"
    )
    genres = models.ManyToManyField(Genre, related_name="books", blank=True)

    class Meta:
        """Метаданные модели Book."""

        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ["title"]

    def __str__(self):
        """Строковое представление книги (название + автор)."""
        return f"{self.title} ({self.author})"

    def decrease_availability(self):
        """Уменьшает количество доступных экземпляров на 1."""
        if self.available_copies > 0:
            self.available_copies -= 1
            self.save()

    def increase_availability(self):
        """Увеличивает количество доступных экземпляров на 1."""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.save()
