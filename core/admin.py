from django.contrib import admin
from .models import Category, Product, ProductImage, HotDeal, Brand

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'slug', 'is_featured']
    list_filter = ['is_featured', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['parent__name', 'name']

    # Optional: nested look in admin list
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('parent')

    def parent_name(self, obj):
        return obj.parent.name if obj.parent else '-'
    parent_name.short_description = 'Parent Category'



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'old_price', 'discount_percent',
        'stock_quantity', 'status', 'is_featured', 'created_at', 'is_active'
    ]
    list_filter = ['category', 'status', 'is_featured', 'is_active']
    search_fields = ['name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}  # auto slug from name
    list_editable = ['price', 'is_active', 'is_featured']
    ordering = ['-created_at']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'is_banner', 'sort_order']
    list_filter = ['is_banner']
    search_fields = ['product__name']


@admin.register(HotDeal)
class HotDealAdmin(admin.ModelAdmin):
    list_display = ['product', 'special_price', 'start_date', 'end_date']
    search_fields = ['product__name']
    list_filter = ['start_date', 'end_date']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)  


from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "type", "discount_amount", "is_active", "expiry_date")
    list_filter = ("type", "is_active")
    search_fields = ("code",)
    ordering = ("-expiry_date",)
