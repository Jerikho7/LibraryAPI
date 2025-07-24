from rest_framework import serializers
from datetime import date


def validate_not_future_date(value):
    """Проверка, что дата не в будущем."""
    if value > date.today():
        raise serializers.ValidationError("Дата не может быть в будущем.")
    return value


def validate_isbn(value):
    """Проверка, что ISBN начинается с 978/979 и состоит из 13 цифр."""
    if not value.isdigit() or len(value) != 13:
        raise serializers.ValidationError("ISBN должен содержать 13 цифр.")
    if not value.startswith(("978", "979")):
        raise serializers.ValidationError("ISBN должен начинаться с 978 или 979.")
    return value
