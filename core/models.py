from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    @property
    def has_children(self):
        return self.children.exists()



class Product(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('sale', 'Sale'),
        ('regular', 'Regular'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percent = models.PositiveIntegerField(default=0)
    
    stock_quantity = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='regular')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank=True, null=True, related_name='brand')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_discount_price(self):
        """Returns price after discount if available."""
        if self.discount_percent > 0:
            return self.price - (self.price * self.discount_percent / 100)
        return self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_banner = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} Image"


class HotDeal(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='hot_deals')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    special_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Hot Deal: {self.product.name}"



