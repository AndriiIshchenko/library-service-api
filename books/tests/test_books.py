from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from books.models import Book, BookCoverType
from books.serializers import BookSerializer


class BookViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": BookCoverType.SOFT,
            "inventory": 5,
            "daily_fee": "10.00",
        }
        self.book = Book.objects.create(**self.book_data)
        self.url = reverse("books:book-list")

    def test_create_book_admin_user(self):
        self.admin_user = get_user_model().objects.create_user(
            email="test@myproject.com", password="testpass123", is_staff=True
        )
        self.client.force_authenticate(user=self.admin_user)
        new_book_data = {
            "title": "New Test Book",
            "author": "New Test Author",
            "cover": BookCoverType.HARD,
            "inventory": 3,
            "daily_fee": "15.00",
        }
        response = self.client.post(self.url, new_book_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        expected_data = BookSerializer(Book.objects.get(id=response.data["id"])).data
        self.assertEqual(response.data, expected_data)

    def test_create_book_non_admin_user(self):
        self.user = get_user_model().objects.create_user(
            email="test@myproject.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        new_book_data = {
            "title": "Unauthorized Book",
            "author": "Regular User",
            "cover": BookCoverType.SOFT,
            "inventory": 1,
            "daily_fee": "5.00",
        }
        response = self.client.post(self.url, new_book_data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Book.objects.count(), 1)

    def test_partial_update_book(self):
        self.admin_user = get_user_model().objects.create_user(
            email="admin@example.com", password="adminpass123", is_staff=True
        )
        self.client.force_authenticate(user=self.admin_user)

        update_data = {"title": "Updated Test Book", "inventory": 10}
        url = reverse("books:book-detail", kwargs={"pk": self.book.id})
        response = self.client.patch(url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Test Book")
        self.assertEqual(self.book.inventory, 10)
        self.assertEqual(self.book.author, "Test Author")
