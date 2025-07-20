from datetime import date

from rest_framework import serializers
from .models import Author, Book, Genre
from .validators import validate_isbn, validate_not_future_date


class AuthorSerializer(serializers.ModelSerializer):
    birthday = serializers.DateField(validators=[validate_not_future_date])

    class Meta:
        model = Author
        fields = "__all__"

    def validate(self, attrs):
        birthday = attrs.get("birthday")
        if birthday:
            age = (date.today() - birthday).days // 365
            if age < 12:
                raise serializers.ValidationError("Автор должен быть старше 10 лет.")
        return attrs

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "description"]


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), source="author", write_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, write_only=True, source="genres"
    )
    isbn = serializers.CharField(validators=[validate_isbn])

    class Meta:
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
            "genre_ids"
        ]

    def validate(self, attrs):
        if attrs["available_copies"] > attrs["total_copies"]:
            raise serializers.ValidationError("Доступных экземпляров не может быть больше общего количества.")
        return attrs
