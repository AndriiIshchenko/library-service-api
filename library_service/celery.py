from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")

app = Celery("library_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


app.conf.beat_schedule = {
    "daily_notify_overdue_borrowings": {
        "task": "notify_overdue",
        "schedule": crontab(hour=9, minute=0),
    },
    "expire_pending_payments_check": {
        "task": "expire_pending_payments",
        "schedule": crontab(minute="*/1"),
    },
}
