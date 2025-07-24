from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from users.permissions import IsLibrarianOrReadOnly
from .models import Author, Book, Genre
from .paginators import Paginator
from .serializers import AuthorSerializer, BookSerializer, GenreSerializer
from django_filters.rest_framework import DjangoFilterBackend


class AuthorViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с авторами книг.

    Предоставляет стандартные CRUD-операции:
    - create (POST): создание нового автора (только для библиотекарей)
    - list (GET): список всех авторов
    - retrieve (GET): получение конкретного автора
    - update (PUT/PATCH): обновление автора (только для библиотекарей)
    - destroy (DELETE): удаление автора (только для библиотекарей)

    Attributes:
        queryset (QuerySet): Набор всех авторов.
        serializer_class (AuthorSerializer): Сериализатор для авторов.
        permission_classes (list): Права доступа (IsLibrarianOrReadOnly).
        pagination_class (Paginator): Класс пагинации.
    """

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    pagination_class = Paginator


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с жанрами книг.

    Предоставляет стандартные CRUD-операции:
    - create (POST): создание нового жанра (только для библиотекарей)
    - list (GET): список всех жанров
    - retrieve (GET): получение конкретного жанра
    - update (PUT/PATCH): обновление жанра (только для библиотекарей)
    - destroy (DELETE): удаление жанра (только для библиотекарей)

    Attributes:
        queryset (QuerySet): Набор всех жанров.
        serializer_class (GenreSerializer): Сериализатор для жанров.
        permission_classes (list): Права доступа (IsLibrarianOrReadOnly).
        pagination_class (Paginator): Класс пагинации.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    pagination_class = Paginator


class BookViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с книгами.

    Предоставляет стандартные CRUD-операции с дополнительными возможностями:
    - Фильтрация по автору, году издания и жанрам
    - Поиск по названию книги и имени автора

    Attributes:
        queryset (QuerySet): Набор всех книг.
        serializer_class (BookSerializer): Сериализатор для книг.
        permission_classes (list): Права доступа (IsLibrarianOrReadOnly).
        pagination_class (Paginator): Класс пагинации.
        filter_backends (list): Бэкенды фильтрации (DjangoFilter, SearchFilter).
        filterset_fields (list): Поля для фильтрации.
        search_fields (list): Поля для поиска.
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    pagination_class = Paginator
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["author", "published_year", "genres"]
    search_fields = ["title", "author__last_name", "author__first_name"]
