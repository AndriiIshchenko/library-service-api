from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from books.models import Book


BORROWINGS_URL = reverse("borrowing:borrowing-list")


class BorrowingViewSetTests(TestCase):
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
        
        expected_return_date = timezone.make_aware(timezone.datetime(2025, 1, 1))

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
