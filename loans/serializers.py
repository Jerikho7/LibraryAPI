from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from books.serializers import BookSerializer
from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Loan._meta.get_field("user").related_model.objects.all(),
        write_only=True,
        source="user",
        required=True
    )
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(queryset=Loan._meta.get_field("book").related_model.objects.all(),
                                                 write_only=True, source="book")

    class Meta:
        model = Loan
        fields = [
            "id", "user", "book", "book_id", "user_id",
            "loan_date", "due_date", "return_date", "renewals_count"
        ]
        read_only_fields = ["loan_date", "due_date", "return_date", "renewals_count"]

    def create(self, validated_data):
        book = validated_data["book"]
        user = validated_data["user"]

        if book.available_copies == 0:
            raise serializers.ValidationError("Нет доступных экземпляров этой книги.")

        if Loan.objects.filter(user=user, book=book, return_date__isnull=True).exists():
            raise serializers.ValidationError("Пользователь уже имеет активную выдачу этой книги.")

        validated_data.update({
            "loan_date": timezone.now().date(),
            "due_date": timezone.now().date() + timedelta(days=14)
        })

        return super().create(validated_data)

    @staticmethod
    def validate_return_date(value):
        from datetime import date
        if value and value < date.today():
            raise serializers.ValidationError("Дата возврата не может быть в прошлом.")
        return value

    def update(self, instance, validated_data):
        if "user" in validated_data or "book" in validated_data:
            raise serializers.ValidationError("Нельзя изменить пользователя или книгу.")
        return super().update(instance, validated_data)
