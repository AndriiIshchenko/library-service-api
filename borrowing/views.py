from django.db import transaction
from django.utils import timezone

from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from borrowing.models import Borrowing

from borrowing.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingReturnBookSerializer,
    BorrowingSerializer,
)
from borrowing.tasks import notify_overdue_borrowings
from payment.models import Payment
from payment.single_payment import create_payment_session


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

    def get_permissions(self, *args, **kwargs):
        permission_classes = [
            IsAuthenticated(),
        ]

        if self.action in ["update", "destroy", "partial_update", "return_book"]:
            permission_classes = [
                IsAdminUser(),
            ]
        return permission_classes

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Borrowing.objects.all().select_related("user", "book")
        else:
            queryset = Borrowing.objects.filter(user=self.request.user).select_related(
                "user", "book"
            )

        is_active = self.request.query_params.get("is_active", None)
        user_id = self.request.query_params.get("user_id", None)
        book_id = self.request.query_params.get("book_id", None)

        if is_active == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)
        if is_active == "false":
            queryset = queryset.filter(actual_return_date__isnull=False)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    @action(detail=True, methods=["PATCH"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        serializer = BorrowingReturnBookSerializer(
            borrowing,
            data={"actual_return_date": timezone.now()},
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                {"message": "Book returned successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="actual_payment")
    def actual_payment(self, request, pk=None):
        """
        Update payment sessions if they are expired 
        for borrowing overdue or regular payment.
        """
        borrowing = self.get_object()
        payment = borrowing.payments.filter(type="payment").first()
        if payment.status == "expired":
            with transaction.atomic():
                payment_session = create_payment_session(borrowing, request)
                Payment.objects.create(
                    borrowing=borrowing,
                    status="pending",
                    type="payment",
                    session_id=payment_session.id,
                    session_url=payment_session.url,
                    money_to_pay=borrowing.money_to_pay,
                )
                return Response(
                    {"message": "Payment session updated."},
                    status=status.HTTP_201_CREATED,
                )

        fee_payment = borrowing.payments.filter(type="fee").first()
        if fee_payment.status == "expired":
            with transaction.atomic():
                payment_session = create_payment_session(borrowing, request)
                Payment.objects.create(
                    borrowing=borrowing,
                    status="pending",
                    type="fee",
                    session_id=payment_session.id,
                    session_url=payment_session.url,
                    money_to_pay=borrowing.overdue_fee,
                )

                return Response(
                    {"message": "Payment session updated."},
                    status=status.HTTP_201_CREATED,
                )

    @action(detail=False, methods=["post"], url_path="notify-overdue")
    def notify_overdue(self, request):
        """
        Send notifications about actual overdue borrowings via telegram.
        """
        notify_overdue_borrowings.delay()
        return Response(
            {"message": "Notification for overdue borrowings has been triggered."},
            status=status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                required=False,
                description="Filter by active borrowings",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                required=False,
                description="Filter by user id",
            ),
            OpenApiParameter(
                name="book_id",
                type=OpenApiTypes.INT,
                required=False,
                description="Filter by book id",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
