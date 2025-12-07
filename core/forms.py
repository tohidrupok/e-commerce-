from django import forms
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'name', 'short_description', 'description',
            'price', 'old_price', 'discount_percent', 'stock_quantity',
            'status', 'is_featured', 'is_active'
        ]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'name', 'short_description', 'description',
            'price', 'old_price', 'discount_percent', 'stock_quantity',
            'status', 'is_featured', 'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # hide original category dropdown
        self.fields['category'].widget = forms.HiddenInput() 

   
   
   
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_banner', 'sort_order']

from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from .models import Product, ProductImage

class ProductImageForm(ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_banner', 'sort_order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Image optional when editing
        if self.instance and self.instance.pk:
            self.fields['image'].required = False






from django.forms import inlineformset_factory
from .models import Product, ProductImage

ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=("image", "alt_text", "is_banner", "sort_order"),
    extra=3,
    can_delete=True
)


from django import forms
from .models import Brand , Category

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name", "logo", "history", "is_active"] 

from django.utils.text import slugify 

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "icon", "is_featured", "parent"]  

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)  
        if commit:
            instance.save()
        return instance
