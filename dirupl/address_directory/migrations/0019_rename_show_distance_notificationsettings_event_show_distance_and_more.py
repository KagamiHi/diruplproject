# Generated by Django 4.2 on 2023-06-05 16:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("address_directory", "0018_notificationsettings_show_distance_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notificationsettings",
            old_name="show_distance",
            new_name="event_show_distance",
        ),
        migrations.RenameField(
            model_name="notificationsettings",
            old_name="show_location",
            new_name="event_show_location",
        ),
    ]
