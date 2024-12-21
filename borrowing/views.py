from django.shortcuts import render

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer


class BorrowingViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = BorrowingSerializer
    queryset = Borrowing.objects.all()
    def get_queryset(self):
        queryset = self.queryset
        is_active = self.request.query_params.get("is_active", None)
        user_id = self.request.query_params.get("user_id", None)
        book_id = self.request.query_params.get("book_id", None)

        if is_active == "true":
            queryset = queryset.filter(actual_return_date=False)
        if is_active == "false":
            queryset = queryset.filter(actual_return_date=True)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if book_id:
            queryset = queryset.filter(book_id=book_id)

        return queryset

    @action(detail=True, methods=["PATCH "], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        borrowing.actual_return_date = timezone.now()
        borrowing.save()
        return Response(
            {"message": "Book returned successfully"}, status=status.HTTP_200_OK
        )
