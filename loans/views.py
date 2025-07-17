from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Loan
from .serializers import LoanSerializer
from users.permissions import IsReader, IsLibrarian


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
            return [IsAuthenticated(), IsReader()]
        if self.action in ["partial_update", "update"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_update(self, serializer):
        loan = self.get_object()
        user = self.request.user
        if user.groups.filter(name="readers").exists() and loan.user != user:
            raise PermissionDenied("Вы можете вернуть только свои книги.")
        serializer.save()
