# Generated by Django 4.2 on 2023-05-26 15:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("address_directory", "0015_rename_guild_id_guildinfo__guild_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="server",
            old_name="playerid",
            new_name="_playerid",
        ),
        migrations.RenameField(
            model_name="server",
            old_name="playertoken",
            new_name="_playertoken",
        ),
    ]