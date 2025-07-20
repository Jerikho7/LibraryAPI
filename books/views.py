from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from users.permissions import IsLibrarian
from .models import Author, Book, Genre
from .serializers import AuthorSerializer, BookSerializer, GenreSerializer
from django_filters.rest_framework import DjangoFilterBackend


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["author", "published_year", "genres"]
    search_fields = ["title", "author__last_name", "author__first_name"]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsLibrarian()]
