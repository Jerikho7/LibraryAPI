from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import CharField, ModelSerializer, ValidationError

from users.models import User


class UserSerializer(ModelSerializer):
    """Сериализатор для модели User.

    Сериализует все поля пользователя, включая:
    - Основные данные (email, имя, фамилия)
    - Дополнительные поля (аватар, телефон, город)
    """

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "avatar", "tg_chat_id", "is_active")


class RegisterSerializer(ModelSerializer):
    """Сериализатор для регистрации нового пользователя.

    Позволяет создать пользователя с указанием email, пароля и дополнительных данных.
    Проверяет совпадение паролей и создаёт пользователя с помощью UserManager.

    Attributes:
        password (CharField): Пароль пользователя (только для записи, валидируется).
        password2 (CharField): Подтверждение пароля (для проверки совпадения).

     Methods:
        validate: Проверяет совпадение паролей.
        create: Создаёт нового пользователя с хэшированным паролем.
    """

    password = CharField(write_only=True, required=True, validators=[validate_password])
    password2 = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "password2", "first_name", "last_name", "avatar", "tg_chat_id")

    def validate(self, data):
        """Проверяет, что пароли совпадают.

        Args:
            data (dict): Входные данные сериализатора.

        Raises:
            ValidationError: Если пароли не совпадают.

        Returns:
            dict: Валидированные данные.
        """
        if data["password"] != data["password2"]:
            raise ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data):
        """Создаёт нового пользователя с хэшированным паролем.

        Удаляет поле password2 и использует User.create_user для создания пользователя.

        Args:
            validated_data (dict): Валидированные данные сериализатора.

        Returns:
            User: Созданный пользователь.
        """
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(ModelSerializer):
    """Сериализатор для смены пароля пользователя."""

    old_password = CharField(required=True)
    new_password = CharField(required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("old_password", "new_password")
