from django.contrib import admin
from .models import Author, Book, Genre


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "country", "birthday")
    search_fields = ("last_name", "first_name")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_year", "isbn", "available_copies", "total_copies")
    search_fields = ("title", "isbn")
    list_filter = ("author", "published_year")
