from django.urls import path
from . import views

urlpatterns = [
    path("orders/", views.admin_order_list, name="admin_order_list"),
    path("orders/<int:pk>/", views.admin_order_detail, name="admin_order_detail"),
    path("orders/<int:pk>/update-payment/", views.admin_update_payment, name="admin_update_payment"),
    path('order/<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),

]


