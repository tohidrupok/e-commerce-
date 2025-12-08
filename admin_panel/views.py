from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Order, OrderItem

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



def order_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)

    return render(request, 'order/invoice.html', {
        'order': order,
        'items': items,
    }) 