from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet

router = DefaultRouter()
router.register(r"authors", AuthorViewSet, basename="authors")
router.register(r"books", BookViewSet, basename="books")

urlpatterns = [

] + router.urls
