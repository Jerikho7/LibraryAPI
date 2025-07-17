from rest_framework.routers import DefaultRouter

from loans.apps import LoansConfig
from loans.views import LoanViewSet

app_name = LoansConfig.name

router = DefaultRouter()
router.register(r"loans", LoanViewSet, basename="loans")

urlpatterns = [] + router.urls
