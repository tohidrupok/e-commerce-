from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import *

def home(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    brands = Brand.objects.filter(is_active=True)
    now = timezone.now()
    deals = HotDeal.objects.filter(start_date__lte=now, end_date__gte=now)

    context = {
        'products': products,
        'deals': deals,
        'brands': brands
    }
    return render(request, 'home.html', context)


# --- Updated Category View ---
def get_all_subcategories(category):
    """Recursively get all child subcategories of a category"""
    subcategories = []
    for child in category.children.all():
        subcategories.append(child)
        subcategories += get_all_subcategories(child)
    return subcategories


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # include category + all its subcategories (recursively)
    subcats = get_all_subcategories(category)
    all_category_ids = [category.id] + [c.id for c in subcats]

    # show all products under these categories
    products = Product.objects.filter(category_id__in=all_category_ids, is_active=True).order_by('-created_at')

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category_products.html', context)



def product_quickview(request, pk):
    product = get_object_or_404(Product, pk=pk)
    print(product)
    return render(request, 'product/quickview.html', {'product': product})



def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product/product_details.html', {'product': product})

















from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .models import Product, ProductImage
from .forms import ProductForm, ProductImageFormSet


def product_list(request):
    products = Product.objects.all()
    return render(request, 'admin/product_list.html', {'products': products})
 


# def product_create(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         formset = ProductImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.none())

#         if form.is_valid() and formset.is_valid():
#             product = form.save()

#             for img_form in formset:
#                 if img_form.cleaned_data.get('image'):
#                     image = img_form.save(commit=False)
#                     image.product = product
#                     image.save()

#             return redirect('product_list')

#     else:
#         form = ProductForm()
#         formset = ProductImageFormSet(queryset=ProductImage.objects.none())

#     return render(request, 'admin/product_create.html', {
#         'form': form,
#         'formset': formset,
#     })

from django.http import QueryDict
from django.http import JsonResponse
from .models import Category 


def product_create(request):
    main_categories = Category.objects.filter(parent__isnull=True)

    if request.method == "POST":
        selected_category_id = request.POST.get("final_category")
        print("Selected Category ID:", selected_category_id)
        
        # Copy POST data (because request.POST is immutable)
        post_data = request.POST.copy()
        post_data["category"] = selected_category_id  # Inject category here

        form = ProductForm(post_data)
        formset = ProductImageFormSet(post_data, request.FILES)

        if form.is_valid() and formset.is_valid():
            product = form.save()

            for img in formset:
                if img.cleaned_data.get("image"):
                    image = img.save(commit=False)
                    image.product = product
                    image.save()

            return redirect("product_list")

    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, "admin/product_create.html", {
        "form": form,
        "formset": formset,
        "main_categories": main_categories,
    })


def get_children_categories(request):
    
    parent_id = request.GET.get("parent_id")
    children = Category.objects.filter(parent_id=parent_id).values("id", "name")
    return JsonResponse(list(children), safe=False)
 
 
 

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')


from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductImage
from .forms import ProductForm, ProductImageFormSet




def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()   # handles add/update/delete automatically

            return redirect("product_list")
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(request, "admin/product_edit.html", {
        "form": form,
        "formset": formset,
        "product": product
    })



def admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect("admin_login")
    
    products = Product.objects.all()

    product_count = Product.objects.count()
    category_count = Category.objects.count()
    brand_count = Brand.objects.count()
    return render(request, "admin/dashboard.html", {
        "product_count": product_count,
        "category_count": category_count,
        "brand_count": brand_count,
        'products': products
    })





from django.shortcuts import render, redirect, get_object_or_404
from .models import Brand
from .forms import BrandForm

def brand_list(request):
    brands = Brand.objects.all()
    return render(request, "brand/list.html", {"brands": brands})


def brand_create(request):
    if request.method == "POST":
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("brand_list")
    else:
        form = BrandForm()

    return render(request, "brand/form.html", {"form": form, "title": "Create Brand"})


def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == "POST":
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            return redirect("brand_list")
    else:
        form = BrandForm(instance=brand)

    return render(request, "brand/form.html", {"form": form, "title": "Edit Brand"})


def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    return redirect("brand_list") 



from django.shortcuts import render, redirect, get_object_or_404
from .models import Category
from .forms import CategoryForm

def category_list(request):
    categories = Category.objects.all()
    return render(request, "category/list.html", {"categories": categories})


# def category_create(request):
#     if request.method == "POST":
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("category_list")
#     else:
#         form = CategoryForm()

#     return render(request, "category/form.html", {"form": form, "title": "Create Category"})


def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "category/form.html", {"form": form, "title": "Edit Category"})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect("category_list") 




from django.shortcuts import render, redirect
from .models import Category
from .forms import CategoryForm

from django.http import JsonResponse

def add_category(request):
    level = request.GET.get('level', '1')
    form = CategoryForm(request.POST or None)

    main_categories = Category.objects.filter(parent__isnull=True)
    sub_categories = Category.objects.none()

    if level == "3":
        # If page POSTed with parent main selection, show its subcategories
        main_id = request.POST.get("parent")
        if main_id:
            sub_categories = Category.objects.filter(parent_id=main_id)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("category_list")

    return render(request, "category/form.html", {
        "form": form,
        "level": level,
        "main_categories": main_categories,
        "sub_categories": sub_categories,
        "title": "Add Category"
    })


# API endpoint for AJAX subcategory fetch
def get_subcategories(request):
    main_id = request.GET.get("main_id")
    subs = Category.objects.filter(parent_id=main_id).values("id", "name")
    return JsonResponse(list(subs), safe=False) 




import string
from django.shortcuts import render
from .models import Brand
from django.shortcuts import render, redirect, get_object_or_404


def brand_index(request):
    # Letters A-Z
    letters = list(string.ascii_uppercase)
    
    # Special: 0-9 brands
    digit_brands = Brand.objects.filter(name__regex=r'^[0-9]').order_by('name')
   
    # A-Z groups
    brands_by_letter = {}
    print(brands_by_letter)
    for letter in letters:
        brands_by_letter[letter] = Brand.objects.filter(
            name__istartswith=letter
        ).order_by('name')
    

    context = {
        "digits": digit_brands,
        "letters": letters,
        "brands_by_letter": brands_by_letter,
    }
    return render(request, "brand/brand_index.html", context) 
    

def brand_products(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)

    products = Product.objects.filter(
        brand=brand,
        is_active=True
    )

    context = {
        'brand': brand,
        'products': products
    }
    return render(request, 'category_products.html', context) 



def add_to_cart(request, product_id):
    print("nice")
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.GET.get('qty', 1))
    final_price = float(product.get_discount_price())

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['qty'] += qty
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': final_price,
            'qty': qty
        }

    request.session['cart'] = cart

    # Calculate total quantity and total amount
    total_qty = sum(item['qty'] for item in cart.values())
    total_amount = sum(item['qty'] * item['price'] for item in cart.values())

    # Return JSON for AJAX popup
    return JsonResponse({
        'product_name': product.name,
        'cart_qty': total_qty,
        'cart_total': f"৳{total_amount:,.2f}",
        'cart_items': cart
    })





def cart_view(request):
    cart = request.session.get('cart', {})

    total = sum(item['price'] * item['qty'] for item in cart.values())

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'total': total
    })


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart
    return redirect('cart_view')


def apply_coupon(request):
    code = request.GET.get("code", "").strip()

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Invalid coupon or gift code."})

    if not coupon.is_valid():
        return JsonResponse({"status": "error", "message": "Code expired or inactive."})

    return JsonResponse({
        "status": "success",
        "type": coupon.type,
        "discount": float(coupon.discount_amount),
        "message": f"{coupon.type.capitalize()} applied successfully!"
    }) 


def update_cart(request, key):
    cart = request.session.get("cart", {})
    action = request.GET.get("type")

    if key in cart:

        if action == "plus":
            cart[key]["qty"] += 1

        elif action == "minus":
            if cart[key]["qty"] > 1:
                cart[key]["qty"] -= 1
            else:
                # qty 0 hole remove
                cart.pop(key)

    request.session["cart"] = cart
    return redirect("cart_view")  
