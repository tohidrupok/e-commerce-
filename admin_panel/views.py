from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Order, OrderItem, Product, PaymentHistory
from accounts.models import Profile 
from django.db import transaction


# Check superuser
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

# 1. Superuser: List all orders
# @superuser_required
# def admin_order_list(request):
#     orders = Order.objects.all().order_by('-created_at')
#     return render(request, "order/admin_order_list.html", {"orders": orders})

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum

 
@superuser_required
def admin_order_list(request):
    # Start with all orders
    orders = Order.objects.select_related('user').prefetch_related('items').all()
    
    # Search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(mobile__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Status filter
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        orders = orders.filter(payment_status=status_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['-created_at', 'created_at', '-total', 'total', '-id', 'id']
    if sort_by in valid_sorts:
        orders = orders.order_by(sort_by)
    else:
        orders = orders.order_by('-created_at')
    
    # Calculate total revenue
    total_revenue = orders.aggregate(Sum('total'))['total__sum'] or 0
    
    context = {
        'orders': orders,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'order/admin_order_list.html', context) 


# 2. Superuser: Order detail / Voucher
@superuser_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    return render(request, "order/admin_order_detail.html", {"order": order, "items": items})

# 3. Superuser: Update payment info
def get_payment_status(amount_paid, total):
    if amount_paid >= total:
        return "paid"
    elif amount_paid > 0:
        return "partial paid"
    return "pending"

from django.db.models import F
from django.db import IntegrityError

@superuser_required
def admin_update_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":

        # 🔹 Validate amount
        try:
            amount = float(request.POST.get("amount_paid", 0))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Invalid payment amount.")
            return redirect("admin_update_payment", pk=order.id)

        method = request.POST.get("payment_method")
        txn_id = request.POST.get("payment_transaction_id", "").strip()
        note = request.POST.get("payment_note", "")

        # 🔹 Non-cash must have transaction id
        if method != "cash" and not txn_id:
            messages.error(
                request,
                "Transaction ID is required for non-cash payments."
            )
            return redirect("admin_update_payment", pk=order.id)

        # 🔹 STOCK CHECK (before payment)
        for item in order.items.select_related("product"):

            if not order.is_stock_reduced:

                if item.product.stock_quantity < item.qty:
                    
                    messages.error(
                        request,
                        f"Insufficient stock for {item.product.name}. "
                        f"Available: {item.product.stock_quantity}, "
                        f"Required: {item.qty}"
                    )
                    return redirect("admin_update_payment", pk=order.id)

        # ✅ All validations passed → atomic transaction
        try:
            with transaction.atomic():

                # 🔹 Update order payment info
                order.amount_paid += amount
                order.payment_status = get_payment_status(
                    order.amount_paid, order.total
                )
                order.payment_method = method
                order.payment_transaction_id = txn_id or None
                order.payment_note = note
                order.save()

                # 🔹 Save payment history
                try:
                    PaymentHistory.objects.create(
                        order=order,
                        amount=amount,
                        payment_method=method,
                        transaction_id=txn_id or None,
                        note=note
                    )
                except IntegrityError:
                    messages.error(
                        request,
                        "This Transaction ID already exists. Please use a unique Transaction ID."
                    )
                    raise  # 🔴 MUST: rollback transaction.atomic()

                # 🔹 Reduce stock only once
                if not order.is_stock_reduced:
                    for item in order.items.select_related("product"):
                        if not item.product:
                            continue

                        Product.objects.filter(
                            id=item.product.id
                        ).update(
                            stock_quantity=F("stock_quantity") - item.qty
                        )

                    order.is_stock_reduced = True
                    order.save(update_fields=["is_stock_reduced"])

        except Exception:
            messages.error(
                request,
                "Payment failed."
            )
            return redirect("admin_update_payment", pk=order.id)

        messages.success(request, "Payment added successfully!")
        return redirect("admin_order_detail", pk=order.id)

    return render(
        request,
        "order/admin_update_payment.html",
        {"order": order}
    ) 


@superuser_required
def admin_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        status = request.POST.get("order_status")
        note = request.POST.get("note", "")

        order.order_status = status
        order.note = note
        order.save()

        messages.success(request, "Order status updated successfully!")
        return redirect("admin_order_list")

    return render(request, "order/admin_update_status.html", {"order": order})


@superuser_required
def order_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)

    return render(request, 'order/invoice.html', {
        'order': order,
        'items': items,
    }) 


from django.shortcuts import render, redirect, get_object_or_404
from core.models import Coupon
from django.utils import timezone

@superuser_required
def coupon_list(request):
    coupons = Coupon.objects.all().order_by('-id')
    return render(request, 'coupon/coupon_list.html', {'coupons': coupons})

@superuser_required
def coupon_create(request):
    error = None

    if request.method == 'POST':
        code = request.POST.get('code')

        # UNIQUE CHECK
        if Coupon.objects.filter(code=code).exists():
            error = "This coupon code already exists!"
        else:
            Coupon.objects.create(
                code=code,
                type=request.POST.get('type'),
                discount_amount=request.POST.get('discount_amount'),
                is_active=True if request.POST.get('is_active') == 'on' else False,
                expiry_date=request.POST.get('expiry_date') or None
            )
            return redirect('coupon_list')

    return render(request, 'coupon/coupon_form.html', {'error': error})

@superuser_required
def coupon_edit(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    error = None

    if request.method == 'POST':
        code = request.POST.get('code')

        # UNIQUE CHECK (exclude current object)
        if Coupon.objects.filter(code=code).exclude(id=coupon.id).exists():
            error = "This coupon code already exists!"
        else:
            coupon.code = code
            coupon.type = request.POST.get('type')
            coupon.discount_amount = request.POST.get('discount_amount')
            coupon.is_active = True if request.POST.get('is_active') == 'on' else False
            coupon.expiry_date = request.POST.get('expiry_date') or None
            coupon.save()
            return redirect('coupon_list')

    return render(request, 'coupon/coupon_form.html', {
        'coupon': coupon,
        'error': error
    })


@superuser_required
def coupon_delete(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    coupon.delete()
    return redirect('coupon_list')



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model


User = get_user_model()
 
# ------------------------
# Client List
# ------------------------
def client_list(request):
    query = request.GET.get("q", "")
    clients = User.objects.filter(role="customer")

    if query:
        clients = clients.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    return render(request, "clients/client_list.html", {"clients": clients, "query": query})

# ------------------------
# Add Client
# ------------------------
def client_add(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        user = User.objects.create_user(username=username, email=email, password=password, role="customer")
        user.phone = phone
        user.save()

        messages.success(request, "Client added successfully!")
        return redirect("client_list")

    return render(request, "clients/client_form.html")

# ------------------------
# Edit Client
# ------------------------
def client_edit(request, pk):
    client = get_object_or_404(User, pk=pk, role="customer")
    profile = getattr(client, "profile", None)

    if request.method == "POST":
        client.username = request.POST.get("username")
        client.email = request.POST.get("email")
        client.phone = request.POST.get("phone")
        password = request.POST.get("password")
        if password:
            client.set_password(password)
        client.save()

    
        if profile:
            profile.address = request.POST.get("address")
            profile.save()

        messages.success(request, "Client updated successfully!")
        return redirect("client_list")

    return render(request, "clients/client_form.html", {"client": client, "profile": profile})

# ------------------------
# Delete Client
# ------------------------
def client_delete(request, pk):
    client = get_object_or_404(User, pk=pk, role="customer")
    client.delete()
    messages.success(request, "Client deleted successfully!")
    return redirect("client_list")


def settings_dashboard(request):
    return render(request, 'settings/dashboard.html') 


from django.shortcuts import render, redirect, get_object_or_404
from .models import SiteHeadline

def headline_page(request):
    edit_headline = None

    # EDIT MODE
    edit_id = request.GET.get('edit')
    if edit_id:
        edit_headline = get_object_or_404(SiteHeadline, id=edit_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        is_active = request.POST.get('is_active') == 'on'
        headline_id = request.POST.get('headline_id')

        if headline_id:
            # UPDATE
            headline = get_object_or_404(SiteHeadline, id=headline_id)
            headline.title = title
            headline.is_active = is_active
            headline.save()
        else:
            # CREATE
            SiteHeadline.objects.create(
                title=title,
                is_active=is_active
            )

        return redirect('headline_page')

    headlines = SiteHeadline.objects.order_by('-created_at')
    return render(request, 'headline/page.html', {
        'headlines': headlines,
        'edit_headline': edit_headline
    })


def headline_delete(request, pk):
    headline = get_object_or_404(SiteHeadline, pk=pk)
    headline.delete()
    return redirect('headline_page')





from .models import HomeSliderSection
from .forms import HomeSliderSectionForm
from django.shortcuts import render, redirect

def home_slider_manage(request):
    instance = HomeSliderSection.objects.first()

    if request.method == 'POST':
        form = HomeSliderSectionForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('home_slider_manage')
    else:
        form = HomeSliderSectionForm(instance=instance)

    return render(request, 'headline/home_slider_manage.html', {'form': form})


from django.shortcuts import render, get_object_or_404, redirect
from core.models import CategoryAttribute, ProductAttributeValue
from django import forms

# =============================
# FORMS
# =============================
class CategoryAttributeForm(forms.ModelForm):
    class Meta:
        model = CategoryAttribute
        fields = ['category', 'name']


class ProductAttributeValueForm(forms.ModelForm):
    class Meta:
        model = ProductAttributeValue
        fields = ['product', 'attribute', 'value']


# =============================
# CATEGORY ATTRIBUTE VIEWS
# =============================
def categoryattribute_list(request):
    attributes = CategoryAttribute.objects.all()
    return render(request, 'category/categoryattribute_list.html', {'attributes': attributes})


def categoryattribute_add(request):
    if request.method == 'POST':
        form = CategoryAttributeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categoryattribute_list')
    else:
        form = CategoryAttributeForm()
    return render(request, 'category/categoryattribute_form.html', {'form': form})


def categoryattribute_edit(request, pk):
    obj = get_object_or_404(CategoryAttribute, pk=pk)
    if request.method == 'POST':
        form = CategoryAttributeForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('categoryattribute_list')
    else:
        form = CategoryAttributeForm(instance=obj)
    return render(request, 'category/categoryattribute_form.html', {'form': form, 'object': obj})


def categoryattribute_delete(request, pk):
    obj = get_object_or_404(CategoryAttribute, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('categoryattribute_list')
    return redirect('categoryattribute_list')  # JS confirm handles deletion


# =============================
# PRODUCT ATTRIBUTE VALUE VIEWS
# =============================
def productattributevalue_list(request):
    product_attributes = ProductAttributeValue.objects.all()
    return render(request, 'category/productattributevalue_list.html', {'product_attributes': product_attributes})


def productattributevalue_add(request):
    if request.method == 'POST':
        form = ProductAttributeValueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productattribute_list')
    else:
        form = ProductAttributeValueForm()
    return render(request, 'category/productattributevalue_form.html', {'form': form})


def productattributevalue_edit(request, pk):
    obj = get_object_or_404(ProductAttributeValue, pk=pk)
    if request.method == 'POST':
        form = ProductAttributeValueForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('productattribute_list')
    else:
        form = ProductAttributeValueForm(instance=obj)
    return render(request, 'category/productattributevalue_form.html', {'form': form, 'object': obj})


def productattributevalue_delete(request, pk):
    obj = get_object_or_404(ProductAttributeValue, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('productattribute_list')
    return redirect('productattribute_list')
