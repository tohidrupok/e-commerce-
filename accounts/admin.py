from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("role", "phone", "avatar")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("role", "phone")}),
    )
    list_display = ("username", "email", "phone", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
