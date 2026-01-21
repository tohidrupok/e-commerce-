from django.urls import path
from . import views

urlpatterns = [
    path("orders/", views.admin_order_list, name="admin_order_list"),
    path("orders/<int:pk>/", views.admin_order_detail, name="admin_order_detail"),
    path("orders/<int:pk>/update-payment/", views.admin_update_payment, name="admin_update_payment"),
    path("orders/<int:pk>/update-status/", views.admin_update_status, name="admin_update_status"),
    path('order/<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),

    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/create/', views.coupon_create, name='coupon_create'),
    path('coupons/edit/<int:id>/', views.coupon_edit, name='coupon_edit'),
    path('coupons/delete/<int:id>/', views.coupon_delete, name='coupon_delete'),

    path("clients/", views.client_list, name="client_list"),
    path("clients/add/", views.client_add, name="client_add"),
    path("clients/<int:pk>/edit/", views.client_edit, name="client_edit"),
    path("clients/<int:pk>/delete/", views.client_delete, name="client_delete"),

    path('settings/', views.settings_dashboard, name='settings_dashboard'), 
    path('headline/', views.headline_page, name='headline_page'),
    path('headline/delete/<int:pk>/', views.headline_delete, name='headline_delete'),
    path('home-slider/', views.home_slider_manage, name='home_slider_manage'),

    path('attributes/', views.categoryattribute_list, name='categoryattribute_list'),
    path('attributes/add/', views.categoryattribute_add, name='categoryattribute_add'),
    path('attributes/<int:pk>/edit/', views.categoryattribute_edit, name='categoryattribute_edit'),
    path('attributes/<int:pk>/delete/', views.categoryattribute_delete, name='categoryattribute_delete'),

    # =============================
    # PRODUCT ATTRIBUTE VALUE
    # =============================
    path('product-attributes/', views.productattributevalue_list, name='productattribute_list'),
    path('product-attributes/add/', views.productattributevalue_add, name='productattribute_add'),
    path('product-attributes/<int:pk>/edit/', views.productattributevalue_edit, name='productattribute_edit'),
    path('product-attributes/<int:pk>/delete/', views.productattributevalue_delete, name='productattribute_delete'),

]


