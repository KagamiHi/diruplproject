# Generated by Django 4.2 on 2023-05-18 10:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("address_directory", "0007_server_delete_condata"),
    ]

    operations = [
        migrations.AddField(
            model_name="server",
            name="server_num",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
