# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('product/quickview/<int:pk>/', views.product_quickview, name='product_quickview'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

]
