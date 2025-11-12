from .models import Category

def categories_menu(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    return {'menu_categories': categories}
