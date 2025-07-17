from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (
    RegisterView,
    ChangePasswordView,
    UserViewSet,
    ModeratorUserViewSet,
)

from rest_framework.permissions import AllowAny

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"profile", UserViewSet, basename="user-profile")
router.register(r"moderator/users", ModeratorUserViewSet, basename="moderator-users")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]

urlpatterns += router.urls
