from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsLibrarian, IsReader
from .models import Loan
from .serializers import LoanSerializer


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="librarians").exists():
            return Loan.objects.all()
        return Loan.objects.filter(user=user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsLibrarian()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsLibrarian()]
        if self.action == "renew_loan":
            return [IsAuthenticated(), IsReader()]
        return [IsAuthenticated()]

    @action(methods=["patch"], detail=True, url_path="renew")
    def renew_loan(self, request, pk=None):
        """Читатель продлевает срок книги (не более 3 раз)."""
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
        """Библиотекарь отмечает возврат книги."""
        loan = self.get_object()
        if not request.user.groups.filter(name="librarians").exists():
            return Response({"detail": "Только библиотекарь может отметить возврат."}, status=status.HTTP_403_FORBIDDEN)
        loan.mark_returned()
        return Response(LoanSerializer(loan).data)
