from django.urls import path, include
from . import views

urlpatterns = [
    path("register/", views.customer_register, name="customer_register"),
    path("login/", views.customer_login, name="customer_login"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("logout/", views.logout_view, name="logout"),

    # Guest checkout endpoint
    path("guest-checkout/", views.guest_checkout, name="guest_checkout"),

    # allauth social URLs (signup/login with social providers)
    path("social/", include("allauth.urls")),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]
