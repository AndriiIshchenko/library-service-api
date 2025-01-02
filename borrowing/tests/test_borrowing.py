from unittest.mock import MagicMock, patch
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from borrowing.models import Borrowing
from books.models import Book, BookCoverType
from payment.models import Payment


BORROWINGS_URL = reverse("borrowing:borrowing-list")


def get_borrowing_detail_url(borrowing):
    return reverse("borrowing:borrowing-detail", args=[borrowing.id])


class BorrowingViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="testuser@library.com", password="testpass123"
        )
        self.user2 = get_user_model().objects.create_user(
            email="user2@library.com", password="testpass321"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@library.com", password="admin123"
        )

        self.book = Book.objects.create(
            title="Test Book", author="Test Author", inventory=5
        )
        self.book2 = Book.objects.create(
            title="Another Book", author="Another Author", inventory=3
        )

        expected_return_date = timezone.now() + timezone.timedelta(days=7)

        self.borrowing1 = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=expected_return_date,
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.admin_user,
            book=self.book,
            expected_return_date=expected_return_date,
        )
        self.borrowing3 = Borrowing.objects.create(
            user=self.user2,
            book=self.book2,
            expected_return_date=timezone.now() + timezone.timedelta(days=7),
        )

    def test_list_all_borrowings_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_users_borrowings(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_active_borrowings(self):
        self.client.force_authenticate(user=self.user)
        active_borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now() + timezone.timedelta(days=7),
        )
        inactive_borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now() + timezone.timedelta(days=7),
            actual_return_date=timezone.now(),
        )

        response = self.client.get(BORROWINGS_URL + "?is_active=true")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # active_borrowing and self.borrowing1
        self.assertIn(active_borrowing.id, [item["id"] for item in response.data])
        self.assertNotIn(inactive_borrowing.id, [item["id"] for item in response.data])

    def test_filter_borrowings_by_user_id(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(BORROWINGS_URL + f"?user_id={self.user.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing1.id)

        response = self.client.get(BORROWINGS_URL + f"?user_id={self.user2.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing3.id)

    def test_filter_borrowings_by_book_id(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(BORROWINGS_URL + f"?book_id={self.book.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(self.borrowing1.id, [item["id"] for item in response.data])
        self.assertIn(self.borrowing2.id, [item["id"] for item in response.data])
        self.assertNotIn(self.borrowing3.id, [item["id"] for item in response.data])

        response = self.client.get(BORROWINGS_URL + f"?book_id={self.book2.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing3.id)


class BorrowingCreateReturnTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="testpass123"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            daily_fee=Decimal("5.00"),
            cover=BookCoverType.HARD,
            inventory=5,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now() + timezone.timedelta(days=7),
        )

    @patch("borrowing.serializers.create_payment_session")
    @patch("borrowing.tasks.notify_new_borrowing.delay")
    def test_create_borrowing(
        self, mock_notify_new_borrowing, mock_create_payment_session
    ):
        self.client.force_authenticate(user=self.user)
        session = MagicMock()
        session.id = "test_session_id"
        session.url = "https://test.com/checkout"
        mock_create_payment_session.return_value = session

        borrowing_data = {
            "user": self.user.id,
            "book": self.book.id,
            "expected_return_date": timezone.now() + timezone.timedelta(days=7),
        }
        response = self.client.post(BORROWINGS_URL, borrowing_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 2)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

        # mock_create_payment_session.assert_called_once_with()
        # mock_notify_new_borrowing.delay.assert_called_once_with()
        new_borrowing = Borrowing.objects.latest("id")
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertEqual(payment.borrowing, new_borrowing)
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.type, "payment")
        self.assertEqual(payment.session_id, "test_session_id")
        self.assertEqual(payment.session_url, "https://test.com/checkout")

    def test_return_book(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            get_borrowing_detail_url(self.borrowing) + "return/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    def test_return_book_by_user_denied(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_borrowing_detail_url(self.borrowing) + "return/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_return_book_already_returned(self):
        self.client.force_authenticate(user=self.admin_user)
        self.borrowing.actual_return_date = timezone.now()
        self.borrowing.save()
        response = self.client.patch(
            get_borrowing_detail_url(self.borrowing) + "return/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This book has already been returned.", str(response.data))
