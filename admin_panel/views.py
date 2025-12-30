from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Order, OrderItem
from accounts.models import Profile 

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
@superuser_required
def admin_update_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        amount_paid = float(request.POST.get("amount_paid", 0))
        status = request.POST.get("payment_status")
        transaction_id = request.POST.get("payment_transaction_id", "")

        order.amount_paid = amount_paid
        order.payment_status = status
        order.payment_transaction_id = transaction_id
        order.save()

        messages.success(request, "Payment info updated successfully!")
        return redirect("admin_order_detail", pk=order.id)

    return render(request, "order/admin_update_payment.html", {"order": order})

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
