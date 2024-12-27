from decimal import Decimal

from django.db import models
from django_enum import EnumField


class BookCoverType(models.TextChoices):
    HARD = "Hardcover"
    SOFT = "Paperback"


class Book(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    author = models.CharField(max_length=120, blank=False, null=False)
    daily_fee = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), blank=True, null=False
    )
    cover = EnumField(BookCoverType, null=True, blank=True)
    inventory = models.PositiveSmallIntegerField(default=0, blank=True, null=False)

    def __str__(self):
        return f"{self.title} by {self.author}"
