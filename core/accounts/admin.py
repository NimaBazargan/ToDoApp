from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class CustomUserAdmin(UserAdmin):
    """
    This is how to display User model in admin
    """
    model = User
    list_display = ("email", "is_superuser", "is_active","is_verified",)
    list_filter = ("email", "is_superuser", "is_active","is_verified",)
    search_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        ('Authentication', {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser","is_verified")}),
        ("group permission", {"fields": ("groups", "user_permissions")}),
        ("important date", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "is_superuser", "is_verified"
            )}
        ),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
