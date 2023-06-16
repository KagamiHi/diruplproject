from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("login","discord_user_id")



class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("login",)