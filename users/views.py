from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from config import settings
from users.models import User
from users.permissions import IsModerator

from users.serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer


class RegisterView(CreateAPIView):
    """API для регистрации нового пользователя.

    Доступные методы:
    - POST: Создать нового пользователя
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        self.send_welcome_email(user.email)

    def send_welcome_email(self, user_email):
        try:
            subject = "Добро пожаловать!"
            message = "Спасибо за регистрацию!"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user_email]

            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Ошибка отправки: {e}")


class ChangePasswordView(UpdateAPIView):
    """
    Контроллер для смены пароля пользователя.
    Пользователь должен передать old_password и new_password.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": ["Неверный текущий пароль"]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"detail": "Пароль успешно изменён"}, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    """
    Контроллер для работы с профилем пользователя (только свой профиль).
    Пользователь может:
    - просматривать
    - редактировать
    - деактивировать (is_active = False)
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id, is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Метод не разрешён. Используйте /register/ для создания пользователя."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(methods=["get", "patch", "delete"], detail=False, url_path="me")
    def me(self, request):
        user = request.user

        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method == "PATCH":
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == "DELETE":
            user.is_active = False
            user.save()
            return Response({"detail": "Профиль удален."}, status=status.HTTP_204_NO_CONTENT)


class ModeratorUserViewSet(ModelViewSet):
    """
    Модераторский доступ:
    - Видит всех пользователей.
    - Удаляет только неактивных.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            return Response({"detail": "Нельзя удалить активного пользователя."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({"detail": "Пользователь удален."}, status=status.HTTP_204_NO_CONTENT)


class ReadOnlyUserViewSet(ReadOnlyModelViewSet):
    """
    Библиотекари и модераторы могут просматривать всех пользователей.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        user = self.request.user
        if user.groups.filter(name__in=["librarians", "moderators"]).exists():
            return [IsAuthenticated()]
        return []
