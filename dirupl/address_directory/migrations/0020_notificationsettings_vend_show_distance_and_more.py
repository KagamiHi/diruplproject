# Generated by Django 4.2 on 2023-06-05 16:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "address_directory",
            "0019_rename_show_distance_notificationsettings_event_show_distance_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationsettings",
            name="vend_show_distance",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="notificationsettings",
            name="vend_show_location",
            field=models.BooleanField(default=False),
        ),
    ]
