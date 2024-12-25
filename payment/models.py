from decimal import Decimal

from django.db import models
from django_enum import EnumField

from borrowing.models import Borrowing


class PaymentStaus(models.TextChoices):
    PENDING = "pending"
    PAID = "paid"


class PaymentType(models.TextChoices):
    PAYMENT = "payment"
    FINE = "fine"


class Payment(models.Model):
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    status = EnumField(PaymentStaus, null=True, blank=True)
    type = EnumField(PaymentType, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    session_url = models.URLField(null=True, blank=True)
    money_to_pay = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), blank=True, null=False
    )
