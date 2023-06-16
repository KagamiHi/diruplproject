from rest_framework import serializers
from dirupl.address_directory.models import NotificationSettings


class NotificationSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationSettings
        fields = ['event_show_location', 'event_show_distance', 'vend_show_location', 'vend_show_distance']