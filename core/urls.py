# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('product/quickview/<int:pk>/', views.product_quickview, name='product_quickview'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('products/add/', views.product_create, name='product_add'),
    path('products/', views.product_list, name='product_list'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path("categories/get_children/", views.get_children_categories, name="get_children_categories"),


    path('my-admin/', views.admin_dashboard, name='admin_dashboard'),


    path("brands/", views.brand_list, name="brand_list"),
    path("brands/create/", views.brand_create, name="brand_create"),
    path("brands/edit/<int:pk>/", views.brand_edit, name="brand_edit"),
    path("brands/delete/<int:pk>/", views.brand_delete, name="brand_delete"),
    path("brands/list/", views.brand_index, name="brand_index"),
    path('brand/<int:brand_id>/', views.brand_products, name='brand_products'), 
    
    path("categories/", views.category_list, name="category_list"),
    # path("categories/create/", views.category_create, name="category_create"),
    path("categories/edit/<int:pk>/", views.category_edit, name="category_edit"),
    path("categories/delete/<int:pk>/", views.category_delete, name="category_delete"),
    
    path("categories/create/", views.add_category, name="add_category"),
    path("categories/get_subcategories/", views.get_subcategories, name="get_subcategories"),


    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("update-cart/<str:key>/", views.update_cart, name="update_cart"),

    # path("checkout/", views.checkout, name="checkout"),
    # path("confirm-order/", views.confirm_order, name="confirm_order"),

    path("checkout/", views.checkout, name="checkout"),
    path("success/", views.success_page, name="success_page"),
        

]
