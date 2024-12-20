from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = BookSerializer()
    queryset = Book.objects.all()
    permission_classes = [IsAdminUser,]
