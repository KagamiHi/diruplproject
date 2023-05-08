from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dirupl.users.managers import CustomUserManager
from django.db import models

from dirupl.common.models import UUIDModel

class CustomUser(AbstractBaseUser, PermissionsMixin , UUIDModel):
    discord_user_id = models.IntegerField(null=True, blank=True, unique=True)
    login = models.CharField(max_length=40, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "login"

    objects = CustomUserManager()

    def __str__(self):
        return self.login