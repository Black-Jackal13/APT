# Generated by Django 5.1.7 on 2025-03-28 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("APT_Django", "0003_raceseason_ongoing"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="player",
            name="password",
        ),
    ]
