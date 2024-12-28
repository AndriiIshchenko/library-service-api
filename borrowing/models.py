from django.utils import timezone
from django.db import models
from django.db.models.constraints import CheckConstraint, Q


OVERDUE_FEE_MULTIPLIER = 3


class Borrowing(models.Model):
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="borrowings"
    )
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="borrowings"
    )
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField(null=False, blank=False)
    actual_return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} borrowed {self.book}"

    @property
    def expected_days(self):
        days_borrowed = (
            self.expected_return_date.date() - self.borrow_date.date()
        ).days
        return days_borrowed

    @property
    def money_to_pay(self):
        amount = self.book.daily_fee * self.expected_days
        return amount

    @property
    def overdue_days(self):
        if self.actual_return_date:
            overdue_days = (
                self.actual_return_date.date() - self.expected_return_date.date()
            ).days
        else:
            overdue_days = (
                timezone.now().date() - self.expected_return_date.date()
            ).days
        return max(overdue_days, 0)

    @property
    def overdue_fee(self):
        overdue_fee = self.book.daily_fee * OVERDUE_FEE_MULTIPLIER * self.overdue_days
        return overdue_fee

    class Meta:
        ordering = ["-borrow_date"]
        constraints = [
            CheckConstraint(
                check=Q(expected_return_date__gt=models.F("borrow_date")),
                name="expected_return_date_after_borrow_date",
            )
        ]
