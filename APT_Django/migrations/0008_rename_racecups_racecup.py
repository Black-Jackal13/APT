# Generated by Django 5.1.7 on 2025-05-20 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("APT_Django", "0007_racecups_cupscore_race_race_cup"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="RaceCups",
            new_name="RaceCup",
        ),
    ]
