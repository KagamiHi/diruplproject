from rest_framework import serializers
from dirupl.users.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['discord_user_id', 'login']
