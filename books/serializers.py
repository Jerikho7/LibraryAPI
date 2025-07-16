from datetime import date

from rest_framework import serializers
from .models import Author, Book
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


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source="author",
        write_only=True
    )
    isbn = serializers.CharField(validators=[validate_isbn])

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "author_id", "published_year", "isbn",
            "total_copies", "available_copies", "description"
        ]

    def validate(self, attrs):
        if attrs["available_copies"] > attrs["total_copies"]:
            raise serializers.ValidationError("Доступных экземпляров не может быть больше общего количества.")
        return attrs
