# Generated by Django 4.2 on 2023-05-06 07:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_rename_cis_staff_customuser_is_staff"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="discord_user_id",
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]