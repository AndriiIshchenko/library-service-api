from django.db import models
from django.db.models.constraints import CheckConstraint, Q


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

    class Meta:
        ordering = ["-borrow_date"]
        constraints = [
            CheckConstraint(
                check=Q(expected_return_date__gt=models.F("borrow_date")),
                name="expected_return_date_after_borrow_date",
            )
        ]
