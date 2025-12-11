from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.utils import timezone
from .models import *
from accounts.forms import GuestCheckoutForm
from accounts.utils import generate_username_from_phone, generate_unique_username
import re
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

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


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product/product_details.html', {'product': product})

# def product_detail(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     return render(request, 'product/product_details.html', {'product': product})



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
            product = form.save()  # specifications saved automatically

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


# def checkout(request):
#     cart = request.session.get("cart", {})

#     if not cart:
#         return redirect("cart_view")

#     subtotal = sum(item['price'] * item['qty'] for item in cart.values())

#     # Default Delivery Charges
#     delivery = {
#         "home": 60,
#         "pickup": 0,
#         "express": 300
#     }

#     return render(request, "order/checkout.html", {
#         "cart": cart,
#         "subtotal": subtotal,
#         "delivery": delivery,
#     })


# def checkout(request):
#     cart = request.session.get("cart", {})
#     if not cart:
#         return redirect("cart_view")

#     subtotal = sum(item['price'] * item['qty'] for item in cart.values())
#     delivery = {"home": 60, "pickup": 0, "express": 300}

#     # ---------------------------------------
#     # If user not logged in → process guest form
#     # ---------------------------------------
#     if not request.user.is_authenticated:
#         if request.method == "POST" and "guest_submit" in request.POST:
#             form = GuestCheckoutForm(request.POST)
#             if form.is_valid():
#                 phone = form.cleaned_data["phone"].strip()
#                 name = form.cleaned_data.get("name") or ""
#                 email = form.cleaned_data.get("email") or ""

#                 try:
#                     user = User.objects.get(phone=phone)
#                 except User.DoesNotExist:
#                     base = generate_username_from_phone(phone)
#                     username = generate_unique_username(User, base)
#                     user = User.objects.create(
#                         username=username,
#                         email=email,
#                         phone=phone,
#                         role="customer"
#                     )
#                     user.set_unusable_password()

#                     if name:
#                         parts = name.split()
#                         user.first_name = parts[0]
#                         if len(parts) > 1:
#                             user.last_name = " ".join(parts[1:])
#                     user.save()

#                 login(request, user,
#                       backend="django.contrib.auth.backends.ModelBackend")

#                 return redirect("checkout")
#         else:
#             form = GuestCheckoutForm()
#     else:
#         form = None  # Logged in user doesn't need guest form

#     return render(request, "order/checkout.html", {
#         "cart": cart,
#         "subtotal": subtotal,
#         "delivery": delivery,
#         "guest_form": form,
#     }) 



# def generate_username_from_phone(phone):
#     return "user" + phone[-6:]

# def generate_unique_username(model, base):
#     username = base
#     i = 1
#     while model.objects.filter(username=username).exists():
#         username = f"{base}{i}"
#         i += 1
#     return username





# def checkout(request):
#     print("1st duckha")
#     cart = request.session.get("cart", {})
#     if not cart:
#         return redirect("cart_view")

#     subtotal = sum(item['price'] * item['qty'] for item in cart.values())
#     delivery = {"home": 60, "pickup": 0, "express": 300}

#     guest_form = None

#     # ---------------- Guest login/create ----------------
#     if not request.user.is_authenticated:
#         print("2nd duckha")
#         if request.method == "POST":
#             print("3rd duckha")
#             guest_form = GuestCheckoutForm(request.POST)
#             print(guest_form)
#             if guest_form.is_valid():
#                 print("4th duckha")
#                 phone = guest_form.cleaned_data["phone"].strip()
#                 name = guest_form.cleaned_data.get("name") or ""
#                 email = guest_form.cleaned_data.get("email") or ""

#                 # Check if user exists
#                 try:
#                     user = User.objects.get(phone=phone)
#                 except User.DoesNotExist:
#                     print("5th duckha")
#                     base = generate_username_from_phone(phone)
#                     username = generate_unique_username(User, base)
#                     user = User.objects.create(
#                         username=username,
#                         email=email or "",
#                         phone=phone,
#                         role="customer"
#                     )
#                     user.set_unusable_password()
#                     if name:
#                         parts = name.strip().split()
#                         user.first_name = parts[0]
#                         if len(parts) > 1:
#                             user.last_name = " ".join(parts[1:])
#                     user.save()

#                 # Login the guest user
#                 login(request, user, backend="django.contrib.auth.backends.ModelBackend")
#                 return redirect("checkout")  # reload page as logged-in

#         else:
#             guest_form = GuestCheckoutForm()

#         return render(request, "order/checkout.html", {
#             "cart": cart,
#             "subtotal": subtotal,
#             "delivery": delivery,
#             "guest_form": guest_form,
#         })

#     # ---------------- Logged-in checkout ----------------
#     # Here you can render your normal checkout form
#     return render(request, "order/checkout.html", {
#         "cart": cart,
#         "subtotal": subtotal,
#         "delivery": delivery,
#         "guest_form": None,  # not needed for logged-in
#     }) 

























# def confirm_order(request):
#     if request.method != "POST":
#         return redirect("checkout")

#     cart = request.session.get("cart", {})
#     if not cart:
#         return redirect("cart_view")

#     subtotal = sum(item["price"] * item["qty"] for item in cart.values())

#     # User Logged In or Guest
#     user = request.user if request.user.is_authenticated else None

#     delivery_method = request.POST.get("delivery_method")
#     delivery_charge = float(request.POST.get("delivery_charge"))
#     payment_method = request.POST.get("payment_method")

#     # Create Order
#     order = Order.objects.create(
#         user=user,
#         first_name=request.POST.get("first_name"),
#         last_name=request.POST.get("last_name"),
#         address=request.POST.get("address"),
#         mobile=request.POST.get("mobile"),
#         email=request.POST.get("email"),
#         upazila=request.POST.get("upazila"),
#         district=request.POST.get("district"),
#         comment=request.POST.get("comment"),

#         delivery_method=delivery_method,
#         delivery_charge=delivery_charge,
#         payment_method=payment_method,

#         subtotal=subtotal,
#         total=subtotal + delivery_charge,
#     )

#     # Order Items Save
#     for key, item in cart.items():
#         OrderItem.objects.create(
#             order=order,
#             product_name=item["name"],
#             price=item["price"],
#             qty=item["qty"],
#         )

#     # Clear Cart After Order
#     del request.session["cart"]

#     return render(request, "order/success.html", {
#         "order": order,
#         "items": order.items.all()
#     })




from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.urls import reverse
from .forms import GuestCheckoutForm, CheckoutForm
from .models import Order, OrderItem

User = get_user_model()

# small helpers to build username
def generate_username_from_phone(phone):
    # ensure phone is string and short unique base
    base = "user" + phone[-6:]
    return base

def generate_unique_username(model, base):
    username = base
    i = 1
    while model.objects.filter(username=username).exists():
        username = f"{base}{i}"
        i += 1
    return username

# def checkout(request):
#     """
#     If user not authenticated -> show guest page (collect phone/name/email).
#     After guest submit -> create/login user and redirect back to checkout_loggedin.
#     If authenticated -> show full checkout form.
#     """
#     cart = request.session.get("cart", {})
#     if not cart:
#         return redirect("cart_view")

#     # subtotal calculation (ensure numbers)
#     subtotal = sum((float(item.get("price", 0)) * int(item.get("qty", 0))) for item in cart.values())
#     delivery_charges = {"home": 60.0, "pickup": 0.0, "express": 300.0}

#     # Guest flow
#     if not request.user.is_authenticated:
#         if request.method == "POST":
#             guest_form = GuestCheckoutForm(request.POST)
#             if guest_form.is_valid():
#                 phone = guest_form.cleaned_data["phone"].strip()
#                 name = guest_form.cleaned_data.get("name") or ""
#                 email = guest_form.cleaned_data.get("email") or ""

#                 # find or create user by phone
#                 try:
#                     user = User.objects.get(phone=phone)
#                 except User.DoesNotExist:
#                     base = generate_username_from_phone(phone)
#                     username = generate_unique_username(User, base)

#                     user = User.objects.create(
#                         username=username,
#                         email=email or "",
#                         phone=phone,
#                     )
#                     user.set_unusable_password()
#                     if name:
#                         parts = name.strip().split()
#                         user.first_name = parts[0]
#                         if len(parts) > 1:
#                             user.last_name = " ".join(parts[1:])
#                     user.save()

#                 # login the user and redirect to same checkout (now authenticated)
#                 login(request, user, backend="django.contrib.auth.backends.ModelBackend")
#                 return redirect("checkout")
#         else:
#             guest_form = GuestCheckoutForm()

#         return render(request, "order/checkout_guest.html", {
#             "guest_form": guest_form,
#             "cart": cart,
#             "subtotal": subtotal,
#             "delivery": delivery_charges,
#         })

#     # Authenticated: show full checkout form (POST will be handled by confirm_order view)
#     # We render checkout page with a CheckoutForm pre-filled
#     initial = {
#         "first_name": request.user.first_name or "",
#         "last_name": request.user.last_name or "",
#         "email": request.user.email or "",
#     }
#     form = CheckoutForm(initial=initial)

#     return render(request, "order/checkout_loggedin.html", {
#         "checkout_form": form,
#         "cart": cart,
#         "subtotal": subtotal,
#         "delivery": delivery_charges,
#     })

# def checkout(request):
#     cart = request.session.get("cart", {})
#     if not cart:
#         return redirect("cart_view")

#     subtotal = sum(item["price"] * item["qty"] for item in cart.values())

#     if request.method == "POST":

#         # if guest
#         if not request.user.is_authenticated:
#             phone = request.POST.get("phone")

#             user, created = User.objects.get_or_create(phone=phone)

#             if created:
#                 username = "user" + phone[-6:]
#                 user.username = username
#                 user.set_unusable_password()
#                 user.save()

#             login(request, user)

#         # Now user is logged in → save order
#         order = Order.objects.create(
#             user=request.user,
#             first_name=request.POST.get("first_name"),
#             last_name=request.POST.get("last_name"),
#             address=request.POST.get("address"),
#             upazila=request.POST.get("upazila"),
#             district=request.POST.get("district"),
#             email=request.POST.get("email"),
#             comment=request.POST.get("comment"),
#             payment_method=request.POST.get("payment_method"),
#             delivery_method=request.POST.get("delivery_method"),
#             delivery_charge=request.POST.get("delivery_charge"),
#             subtotal=subtotal,
#             total=subtotal + int(request.POST.get("delivery_charge")),
#         )

#         for key, item in cart.items():
#             OrderItem.objects.create(
#                 order=order,
#                 product_name=item["name"],  # name -> product_name
#                 price=item["price"],
#                 qty=item["qty"]              # quantity -> qty
#             ) 

#         # for key, item in cart.items():
#         #     OrderItem.objects.create(
#         #         order=order,
#         #         product_id=key,
#         #         name=item["name"],
#         #         quantity=item["qty"],
#         #         price=item["price"],
#         #         total=item["qty"] * item["price"]
#         #     )

#         request.session["cart"] = {}
#         return redirect("success_page")

#     return render(request, "order/checkout.html", {
#         "cart": cart,
#         "subtotal": subtotal,
#     }) 

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from .models import Order, OrderItem

User = get_user_model()

# def checkout(request):
#     cart = request.session.get("cart", {})
#     if not cart:
#         return redirect("cart_view")

#     subtotal = sum(item["price"] * item["qty"] for item in cart.values())

#     if request.method == "POST":

#         # --- Guest user handling ---
#         if not request.user.is_authenticated:
#             phone = request.POST.get("phone")

#             user, created = User.objects.get_or_create(phone=phone)

#             if created:
#                 username = "user" + phone[-6:]
#                 user.username = username
#                 user.set_unusable_password()
#                 user.save()

#             # Fix multiple backends issue
#             backend = 'django.contrib.auth.backends.ModelBackend'  # default Django backend
#             user.backend = backend
#             login(request, user)

#         # --- Save Order ---
#         delivery_charge = float(request.POST.get("delivery_charge", 0)) 

#         mobile = request.POST.get("mobile") or request.POST.get("phone") 
#         print("My Contact: ",mobile)
#         order = Order.objects.create(
#             user=request.user,
#             first_name=request.POST.get("first_name"),
#             last_name=request.POST.get("last_name"),
#             address=request.POST.get("address"),
#             mobile=mobile,
#             upazila=request.POST.get("upazila"),
#             district=request.POST.get("district"),
#             email=request.POST.get("email"),
#             comment=request.POST.get("comment"),
#             payment_method=request.POST.get("payment_method"),
#             delivery_method=request.POST.get("delivery_method"),
#             delivery_charge=delivery_charge,
#             subtotal=subtotal,
#             total=subtotal + delivery_charge,
#         )

#         # --- Save Order Items ---
#         for key, item in cart.items():
#             OrderItem.objects.create(
#                 order=order,
#                 product_name=item["name"],
#                 price=item["price"],
#                 qty=item["qty"]
#             )

#         # --- Clear Cart ---
#         request.session["cart"] = {}

#         return redirect("success_page")

#     return render(request, "order/checkout.html", {
#         "cart": cart,
#         "subtotal": subtotal,
#     }) 

import re

def validate_bd_phone(phone):
    # Trim spaces, just in case
    phone = phone.strip()

    # 1. Contains invalid characters (letters or symbols except +)
    if re.search(r'[^0-9+]', phone):
        return "Phone number can only contain digits or '+' at start."

    # 2. More than one plus sign
    if phone.count('+') > 1:
        return "Phone number can't contain multiple '+' symbols."

    # 3. '+' not at the beginning
    if '+' in phone and not phone.startswith('+'):
        return "Plus sign (+) must be at the beginning only."

    # 4. Handle international format
    if phone.startswith('+'):
        if not phone.startswith('+880'):
            return "International format must start with +880."
        if len(phone) != 14:
            return "International number must be 14 characters (+8801XXXXXXXXX)."
        if not re.fullmatch(r'\+8801[3-9]\d{8}', phone):
            return "Invalid Bangladeshi operator code in international number."
        return None  # valid international

    # 5. Handle local BD format
    if not phone.startswith('01'):
        return "Local Bangladeshi numbers must start with 01."

    if len(phone) != 11:
        return "Local Bangladeshi numbers must be exactly 11 digits."

    if not re.fullmatch(r'01[3-9]\d{8}', phone):
        return "Invalid Bangladeshi operator code."

    # Passed all checks
    return None
 
 
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart_view")

    subtotal = sum(item["price"] * item["qty"] for item in cart.values())

    if request.method == "POST":
        phone = request.POST.get("phone")

        error = validate_bd_phone(phone)
        if error:
            messages.error(request, error)
            return redirect("checkout")
        
        # Guest or logged-in
        if not request.user.is_authenticated:
            phone = request.POST.get("phone")
            user, created = User.objects.get_or_create(phone=phone)
            if created:
                username = "user" + phone[-6:]
                user.username = username
                user.set_unusable_password()
                user.save()
            # Login user
            backend = 'django.contrib.auth.backends.ModelBackend'
            user.backend = backend
            login(request, user)

        # Save order
        delivery_charge = float(request.POST.get("delivery_charge", 0))
        discount = float(request.POST.get("coupon_discount", 0))
        mobile = request.POST.get("phone") or request.POST.get("phone")
        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            address=request.POST.get("address"),
            mobile=mobile,
            upazila=request.POST.get("upazila"),
            district=request.POST.get("district"),
            email=request.POST.get("email"),
            comment=request.POST.get("comment"),
            payment_method=request.POST.get("payment_method"),
            delivery_method=request.POST.get("delivery_method"),
            delivery_charge=delivery_charge,
            subtotal=subtotal,
            discount=discount,
            total=subtotal + delivery_charge - discount 
        )

        for key, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_name=item["name"],
                price=item["price"],
                qty=item["qty"]
            )

        request.session["cart"] = {}
        return redirect("success_page")

    return render(request, "order/checkout.html", {"cart": cart, "subtotal": subtotal}) 

def success_page(request):
    return render(request, "order/success.html") 


# def confirm_order(request):
#     """
#     Accept POST from checkout_loggedin form, validate, create Order+OrderItems, clear cart.
#     """
#     if request.method != "POST":
#         return redirect("checkout")

#     if not request.user.is_authenticated:
#         # safety: only logged-in users should confirm order here
#         return redirect("checkout")

#     cart = request.session.get("cart", {})
#     if not cart:
#         return redirect("cart_view")

#     form = CheckoutForm(request.POST)
#     if not form.is_valid():
#         # re-render loggedin checkout with errors
#         subtotal = sum((float(item.get("price", 0)) * int(item.get("qty", 0))) for item in cart.values())
#         delivery_charges = {"home": 60.0, "pickup": 0.0, "express": 300.0}
#         return render(request, "order/checkout_loggedin.html", {
#             "checkout_form": form,
#             "cart": cart,
#             "subtotal": subtotal,
#             "delivery": delivery_charges,
#         })

#     # valid -> create order
#     cleaned = form.cleaned_data
#     delivery_method = cleaned["delivery_method"]
#     delivery_charge = {"home": 60.0, "pickup": 0.0, "express": 300.0}.get(delivery_method, 0.0)
#     subtotal = sum((float(item.get("price", 0)) * int(item.get("qty", 0))) for item in cart.values())
#     total = subtotal + delivery_charge

#     order = Order.objects.create(
#         user=request.user,
#         first_name=cleaned["first_name"],
#         last_name=cleaned["last_name"],
#         address=cleaned["address"],
#         mobile=cleaned["mobile"],
#         email=cleaned["email"],
#         upazila=cleaned["upazila"],
#         district=cleaned["district"],
#         comment=cleaned.get("comment", ""),
#         delivery_method=delivery_method,
#         delivery_charge=delivery_charge,
#         payment_method=cleaned["payment_method"],
#         subtotal=subtotal,
#         total=total,
#     )

#     # save items
#     for key, item in cart.items():
#         # make sure item has name, price, qty
#         OrderItem.objects.create(
#             order=order,
#             product_name=item.get("name", "Product"),
#             price=float(item.get("price", 0)),
#             qty=int(item.get("qty", 0)),
#         )

#     # clear cart
#     request.session["cart"] = {}

#     # render success
#     return render(request, "order/success.html", {"order": order})