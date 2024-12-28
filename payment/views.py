from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from payment.models import Payment

from payment.serializers import (
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentSerializer,
)
from payment.tasks import notify_success_payment


class PaymentViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    @action(detail=False, methods=["GET"], url_path="success")
    def success(self, request):
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        payment.status = "paid"
        payment.save()
        notify_success_payment(payment.id)
        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="cancel")
    def cancel(self, request):
        return Response(
            {"message": "Payment can be made later, session available for 24h"},
            status=status.HTTP_200_OK,
        )
