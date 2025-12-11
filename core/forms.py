from django import forms
from .models import Product, ProductImage

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = [
#             'category', 'brand', 'name', 'short_description', 'description',
#             'price', 'old_price', 'discount_percent', 'stock_quantity',
#             'status', 'is_featured', 'is_active', 'specifications'
#         ]

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = [
#             'category', 'brand', 'name', 'short_description', 'description',
#             'price', 'old_price', 'discount_percent', 'stock_quantity',
#             'status', 'is_featured', 'is_active', 'specifications'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # hide original category dropdown
#         self.fields['category'].widget = forms.HiddenInput() 

   
from ckeditor.widgets import CKEditorWidget

class ProductForm(forms.ModelForm):
    specifications = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'name', 'short_description', 'description',
            'price', 'old_price', 'discount_percent', 'stock_quantity',
            'status', 'is_featured', 'is_active', 'specifications'
        ] 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # hide original category dropdown
        self.fields['category'].widget = forms.HiddenInput() 

from ckeditor.widgets import CKEditorWidget

class ProductForm(forms.ModelForm):
    specifications = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'name', 'short_description', 'description',
            'price', 'old_price', 'discount_percent', 'stock_quantity',
            'status', 'is_featured', 'is_active', 'specifications'
        ] 

        
   
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



from django import forms

class GuestCheckoutForm(forms.Form):
    phone = forms.CharField(max_length=30, label="Phone", widget=forms.TextInput(attrs={"placeholder": "01XXXXXXXXX"}))
    name = forms.CharField(max_length=150, required=False, label="Full name (optional)")
    email = forms.EmailField(required=False, label="Email (optional)")

class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows":2}))
    mobile = forms.CharField(max_length=20)
    email = forms.EmailField()
    upazila = forms.CharField(max_length=100)
    district = forms.CharField(max_length=100)
    comment = forms.CharField(widget=forms.Textarea(attrs={"rows":2}), required=False)

    DELIVERY_CHOICES = [
        ("home", "Home Delivery - 60৳"),
        ("pickup", "Store Pickup - 0৳"),
        ("express", "Request Express - 300৳"),
    ]
    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("online", "Online Payment"),
        ("pos", "POS on Delivery"),
    ]

    delivery_method = forms.ChoiceField(choices=DELIVERY_CHOICES)
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES)
