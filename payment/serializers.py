from rest_framework import serializers

from borrowing.serializers import BorrowingSerializer
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "borrowing",
            "status",
            "type",
            "created_at",
            "session_id",
            "session_url",
            "money_to_pay",
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    borrowing = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="id",
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "borrowing",
            "status",
            "type",
            "created_at",
            "session_id",
            "session_url",
            "money_to_pay",
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingSerializer()

    class Meta:
        model = Payment
        fields = [
            "id",
            "borrowing",
            "status",
            "type",
            "created_at",
            "session_id",
            "session_url",
            "money_to_pay",
        ]
