# Generated by Django 5.1.7 on 2025-04-11 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("APT_Django", "0004_remove_player_password"),
    ]

    operations = [
        migrations.AddField(
            model_name="race",
            name="race_tier",
            field=models.IntegerField(default=1),
        ),
    ]
