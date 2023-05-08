from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("login", "is_staff", "is_active",)
    list_filter = ("login", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("login", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "login", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("login",)
    ordering = ("login",)


admin.site.register(CustomUser, CustomUserAdmin)