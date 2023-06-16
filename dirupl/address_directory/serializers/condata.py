from rest_framework import serializers
from dirupl.address_directory.models import Server
from .notset import NotificationSettingsSerializer


class ServerSerializer(serializers.Serializer):
    
    name = serializers.CharField(max_length=200)
    desc = serializers.CharField(max_length=200)
    img = serializers.URLField()
    
    class Meta:
        model = Server
        fields = [
            "name", "desc", "img",
        ]

