from django.contrib import admin
from .models import SiteHeadline

@admin.register(SiteHeadline)
class SiteHeadlineAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
