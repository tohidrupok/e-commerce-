from django.contrib import admin
from .models import SiteHeadline

@admin.register(SiteHeadline)
class SiteHeadlineAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)



from django.contrib import admin
from .models import HomeSliderSection

@admin.register(HomeSliderSection)
class HomeSliderSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'created_at')
