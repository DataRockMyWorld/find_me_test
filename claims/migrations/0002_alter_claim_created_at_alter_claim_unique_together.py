# Generated by Django 4.2.11 on 2024-03-13 14:21

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("claims", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="claim",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterUniqueTogether(
            name="claim",
            unique_together={("item", "claimant")},
        ),
    ]