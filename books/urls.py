from django.urls import path, include
from rest_framework import routers

from books.views import BookListView, BookManageViewSet


router = routers.DefaultRouter()


router.register("books", BookListView)
router.register("books-manage", BookManageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "books"
