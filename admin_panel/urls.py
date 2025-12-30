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

]


