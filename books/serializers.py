from datetime import date
from rest_framework import serializers
from .models import Author, Book, Genre
from .validators import validate_isbn, validate_not_future_date


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Author.

    Attributes:
        birthday (DateField): Дата рождения с валидацией на будущие даты.
    """

    birthday = serializers.DateField(validators=[validate_not_future_date])

    class Meta:
        """Метаданные сериализатора Author."""

        model = Author
        fields = "__all__"

    def validate(self, attrs):
        """Проверяет, что возраст автора больше 10 лет.

        Args:
            attrs (dict): Атрибуты для валидации.

        Returns:
            dict: Валидированные атрибуты.

        Raises:
            ValidationError: Если возраст автора меньше 12 лет.
        """
        birthday = attrs.get("birthday")
        if birthday:
            age = (date.today() - birthday).days // 365
            if age < 12:
                raise serializers.ValidationError("Автор должен быть старше 10 лет.")
        return attrs


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        """Метаданные сериализатора Genre."""

        model = Genre
        fields = ["id", "name", "description"]


class BookSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Book.

    Attributes:
        author (AuthorSerializer): Вложенный сериализатор для автора (read-only).
        author_id (PrimaryKeyRelatedField): Поле для установки автора (write-only).
        genres (GenreSerializer): Вложенный сериализатор для жанров (read-only).
        genre_ids (PrimaryKeyRelatedField): Поле для установки жанров (write-only).
        isbn (CharField): Поле ISBN с кастомной валидацией.
    """

    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), source="author", write_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, write_only=True, source="genres"
    )
    isbn = serializers.CharField(validators=[validate_isbn])

    class Meta:
        """Метаданные сериализатора Book."""

        model = Book
        fields = [
            "id",
            "title",
            "author",
            "author_id",
            "published_year",
            "isbn",
            "total_copies",
            "available_copies",
            "description",
            "genres",
            "genre_ids",
        ]

    def validate(self, attrs):
        """Проверяет, что доступных экземпляров не больше общего количества.

        Args:
            attrs (dict): Атрибуты для валидации.

        Returns:
            dict: Валидированные атрибуты.

        Raises:
            ValidationError: Если available_copies > total_copies.
        """
        if attrs["available_copies"] > attrs["total_copies"]:
            raise serializers.ValidationError("Доступных экземпляров не может быть больше общего количества.")
        return attrs

    def validate_isbn(self, value):
        """Валидирует ISBN на соответствие формату и уникальность.

        Args:
            value (str): Значение ISBN для валидации.

        Returns:
            str: Валидный ISBN.

        Raises:
            ValidationError: Если ISBN невалиден или уже существует.
        """
        value = validate_isbn(value)

        instance = getattr(self, "instance", None)
        queryset = Book.objects.filter(isbn=value)

        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            existing = queryset.first()
            raise serializers.ValidationError(
                f"Книга с ISBN {value} уже существует: "
                f"«{existing.title}» (ID: {existing.id}). "
                "Измените ISBN или отредактируйте существующую книгу."
            )

        return value
