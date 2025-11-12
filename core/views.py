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
    print(product)
    return render(request, 'product/product_details.html', {'product': product})
