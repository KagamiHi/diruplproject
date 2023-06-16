from rest_framework import serializers
from dirupl.address_directory.models import Guildinfo
from dirupl.address_directory.serializers import ServerSerializer, NotificationSettingsSerializer

class GuildinfoSerializer(serializers.ModelSerializer):
    server = ServerSerializer()
    notification_settings = NotificationSettingsSerializer()

    class Meta:
        model = Guildinfo

        fields = [
            "id", "name", "server", "notification_settings",
        ]