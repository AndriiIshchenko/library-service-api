# Generated by Django 5.1.4 on 2025-01-01 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="session_url",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
