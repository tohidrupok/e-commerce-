from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

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
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
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
        unique_together = ('parent', 'slug')  # slug unique per parent
        ordering = ['parent__name', 'name']

    def __str__(self):
        # show parent in string optionally
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    @property
    def has_children(self):
        return self.children.exists()

    def save(self, *args, **kwargs):
        # Auto-generate slug based on name + parent
        base_slug = slugify(self.name)
        if self.parent:
            base_slug = f"{slugify(self.parent.name)}-{base_slug}"

        slug = base_slug
        counter = 1
        while Category.objects.filter(parent=self.parent, slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = slug
        super().save(*args, **kwargs) 


class Product(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('sale', 'Sale'),
        ('regular', 'Regular'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    specifications = RichTextField(blank=True, null=True, help_text="Add product specs like Word/Doc style")

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
        
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
        
        

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




from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    COUPON_TYPES = (
        ('coupon', 'Coupon'),
        ('gift', 'Gift Code'),
    )

    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=10, choices=COUPON_TYPES, default='coupon')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True)

    def is_valid(self):
        if not self.is_active:
            return False
        
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        
        return True

    def __str__(self):
        return f"{self.code} ({self.type})"

from django.conf import settings


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True, blank=True )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField()
    mobile = models.CharField(max_length=20)
    email = models.EmailField()

    upazila = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    comment = models.TextField(blank=True, null=True)

    delivery_method = models.CharField(max_length=50)
    delivery_charge = models.FloatField(default=0)

    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(
        max_length=20,
        choices=(
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
            ("partial paid", "partial Paid"),
        ),
        default="pending"
    )
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.FloatField(default=0)  # How much customer has paid

   

    subtotal = models.FloatField()
    discount = models.FloatField(default=0)
    total = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=255)
    price = models.FloatField()
    qty = models.IntegerField()

    def total(self):
        return self.price * self.qty
 

