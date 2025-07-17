from rest_framework import serializers
from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Loan._meta.get_field('book').related_model.objects.all())

    class Meta:
        model = Loan
        fields = ["id", "user", "book", "loan_date", "return_date"]
        read_only_fields = ["id", "loan_date", "user"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        book = validated_data["book"]

        if book.available_copies == 0:
            raise serializers.ValidationError("Нет доступных экземпляров этой книги.")

        if Loan.objects.filter(user=user, book=book, return_date__isnull=True).exists():
            raise serializers.ValidationError("Вы уже взяли эту книгу и не вернули.")

        validated_data["user"] = user
        return super().create(validated_data)

    def validate_return_date(self, value):
        from datetime import date
        if value and value < date.today():
            raise serializers.ValidationError("Дата возврата не может быть в прошлом.")
        return value

    def update(self, instance, validated_data):
        if "user" in validated_data or "book" in validated_data:
            raise serializers.ValidationError("Нельзя изменить пользователя или книгу.")
        return super().update(instance, validated_data)
