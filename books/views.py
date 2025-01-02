from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from books.models import Book
from books.permissions import IsAdminUserOrReadOnly
from books.serializers import BookSerializer


class BookViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = [
        IsAdminUserOrReadOnly,
    ]

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)
