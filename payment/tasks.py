import os
from datetime import timedelta
import requests

from django.utils import timezone

from dotenv import load_dotenv
from celery import shared_task

from .models import Payment, PaymentStatus


load_dotenv()

TELEGRAM_API_URL = (
    f"https://api.telegram.org/bot{os.environ.get("TELEGRAM_BOT_TOKEN")}/sendMessage"
)
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CHAT_ID_2 = os.environ.get("TELEGRAM_CHAT_ID_2")

@shared_task
def notify_success_payment(payment_id):
    payment = Payment.objects.get(id=payment_id)
    message = (
        f"Borrowing: {payment.borrowing.book.title} by {payment.borrowing.user.email}. "
        f"was paid {payment.money_to_pay} USD."
    )
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(TELEGRAM_API_URL, data=data, timeout=5)
    data = {"chat_id": CHAT_ID_2, "text": message}
    response = requests.post(TELEGRAM_API_URL, data=data, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Failed to send a message: {response.text}")




@shared_task(name="expire_pending_payments")
def expire_pending_payments():
    pending_payments = Payment.objects.filter(status="pending")
    for payment in pending_payments:
        if payment.created_at < timezone.now() - timedelta(days=1):
            payment.status = PaymentStatus.EXPIRED
            payment.save()
