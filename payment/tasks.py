from datetime import timedelta
from django.utils import timezone

from celery import shared_task


from dotenv import load_dotenv

from .models import Payment, PaymentStatus

load_dotenv()


@shared_task(name="expire_pending_payments")
def expire_pending_payments():
    pending_payments = Payment.objects.filter(status="pending")
    for payment in pending_payments:
        if payment.created_at < timezone.now() - timedelta(days=1):
            payment.status = PaymentStatus.EXPIRED
            payment.save()
