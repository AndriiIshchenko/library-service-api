import os
from datetime import date, timedelta
import requests

from celery import shared_task


from dotenv import load_dotenv

from .models import Borrowing

load_dotenv()

TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}/sendMessage"
)
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

@shared_task
def notify_new_borrowing(borrowing_id):
    borrowing = Borrowing.objects.get(id=borrowing_id)
    message = (
        f"New borrowing: {borrowing.book.title} by {borrowing.user.email}. "
        f"Expected return date: {borrowing.expected_return_date}."
    )
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(TELEGRAM_API_URL, data=data, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Failed to send a message: {response.text}")


@shared_task(name="notify_overdue")
def notify_overdue_borrowings():
    data = {"chat_id": CHAT_ID, "text": "Working>>>"}
    response = requests.post(TELEGRAM_API_URL, data=data, timeout=5)

    overdue_borrowings = Borrowing.objects.all().filter(
        expected_return_date__lt=date.today() + timedelta(days=2),
        actual_return_date__isnull=True,
    )
    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            message = (
                f"Book '{borrowing.book.title}' is overdue. "
                f"Expected return date: {borrowing.expected_return_date}."
            )
            data = {"chat_id": CHAT_ID, "text": message}
            response = requests.post(TELEGRAM_API_URL, data=data, timeout=5)
            if response.status_code != 200:
                raise Exception(f"Failed to send a message: {response.text}")
    else:
        data = {"chat_id": CHAT_ID, "text": "No overdue borrowings."}
        response = requests.post(TELEGRAM_API_URL, data=data, timeout=5)

    data2 = {"chat_id": CHAT_ID, "text": "Stop>>>"}
    response = requests.post(TELEGRAM_API_URL, data=data2, timeout=5)
    return overdue_borrowings.count()
