from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from books.paginators import Paginator
from users.permissions import IsLibrarian, IsReader
from .models import Loan
from .serializers import LoanSerializer


class LoanViewSet(viewsets.ModelViewSet):
    """ViewSet для управления выдачами книг.

    Предоставляет следующие возможности:
    - Создание, просмотр, обновление и удаление выдач (CRUD)
    - Продление срока возврата книги (для читателей)
    - Отметка возврата книги (для библиотекарей)

    Права доступа:
    - Создание, изменение и удаление: только для библиотекарей
    - Продление: только для читателей
    - Просмотр: читатели видят только свои выдачи, библиотекари - все
    """

    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = Paginator

    def get_queryset(self):
        """Возвращает queryset в зависимости от роли пользователя.

        Returns:
            QuerySet:
                - Для библиотекарей: все выдачи
                - Для читателей: только выдачи текущего пользователя
        """
        user = self.request.user
        if user.groups.filter(name="librarians").exists():
            return Loan.objects.all()
        return Loan.objects.filter(user=user)

    def get_permissions(self):
        """Определяет права доступа в зависимости от действия.

        Returns:
            list: Список классов разрешений для текущего действия.
        """
        if self.action == "create":
            return [IsAuthenticated(), IsLibrarian()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsLibrarian()]
        if self.action == "renew_loan":
            return [IsAuthenticated(), IsReader()]
        return [IsAuthenticated()]

    @action(methods=["patch"], detail=True, url_path="renew")
    def renew_loan(self, request, pk=None):
        """Продлевает срок возврата книги.

        Args:
            request (Request): Объект HTTP-запроса.
            pk (int): Первичный ключ выдачи.

        Returns:
            Response:
                - 200 OK с данными выдачи при успехе
                - 400 Bad Request при достижении лимита продлений
                - 403 Forbidden при попытке продлить чужую книгу
        """
        loan = self.get_object()
        if loan.user != request.user:
            return Response({"detail": "Вы можете продлить только свою книгу."}, status=status.HTTP_403_FORBIDDEN)
        try:
            loan.renew()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LoanSerializer(loan).data)

    @action(methods=["patch"], detail=True, url_path="return")
    def return_book(self, request, pk=None):
        """Отмечает книгу как возвращенную.

        Args:
            request (Request): Объект HTTP-запроса.
            pk (int): Первичный ключ выдачи.

        Returns:
            Response:
                - 200 OK с данными выдачи при успехе
                - 403 Forbidden для пользователей без прав библиотекаря
        """
        loan = self.get_object()
        if not request.user.groups.filter(name="librarians").exists():
            return Response(
                {"detail": "Только библиотекарь может отметить возврат."}, status=status.HTTP_403_FORBIDDEN
            )
        loan.mark_returned()
        return Response(LoanSerializer(loan).data)
