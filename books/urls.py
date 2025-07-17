from rest_framework.routers import DefaultRouter

from .apps import BooksConfig
from .views import AuthorViewSet, BookViewSet

app_name = BooksConfig.name

router = DefaultRouter()
router.register(r"authors", AuthorViewSet, basename="authors")
router.register(r"books", BookViewSet, basename="books")

urlpatterns = [] + router.urls
