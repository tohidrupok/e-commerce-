from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import CustomerRegisterForm, CustomerLoginForm, AdminLoginForm, GuestCheckoutForm
from .utils import generate_username_from_phone, generate_unique_username

User = get_user_model()

# ------------------------
# Customer Registration
# ------------------------
def customer_register(request):
    if request.method == "POST":
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role="customer"
            )
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("home")  # redirect to homepage after registration
    else:
        form = CustomerRegisterForm()

    return render(request, "accounts/customer_register.html", {"form": form})


# ------------------------
# Customer Login
# ------------------------
def customer_login(request):
    if request.method == "POST":
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user and user.is_customer():
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect("home")
            else:
                form.add_error(None, "Invalid credentials or not a customer")
    else:
        form = CustomerLoginForm()
    return render(request, "accounts/customer_login.html", {"form": form})


# ------------------------
# Admin Login
# ------------------------
def admin_login(request):
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user and user.is_admin():
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect("admin_dashboard")  
            else:
                form.add_error(None, "Invalid admin credentials")
    else:
        form = AdminLoginForm()
    return render(request, "accounts/admin_login.html", {"form": form})


# ------------------------
# Guest Checkout
# ------------------------
def guest_checkout(request):
    """
    Guest checkout page:
    - Accepts phone (required), optional name & email.
    - If a user with this phone exists -> logs in.
    - Otherwise create a new User with only phone (no password), role=customer, and auto-create Profile.
    """
    if request.method == "POST":
        form = GuestCheckoutForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"].strip()
            name = form.cleaned_data.get("name") or ""
            email = form.cleaned_data.get("email") or ""

            try:
                user = User.objects.get(phone=phone)
                created = False
            except User.DoesNotExist:
                base = generate_username_from_phone(phone)
                username = generate_unique_username(User, base)
                user = User.objects.create(
                    username=username,
                    email=email or "",
                    phone=phone,
                    role="customer",
                )
                user.set_unusable_password()
                if name:
                    parts = name.strip().split()
                    user.first_name = parts[0]
                    if len(parts) > 1:
                        user.last_name = " ".join(parts[1:])
                user.save()
                created = True

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("checkout")  # redirect to actual checkout page
    else:
        form = GuestCheckoutForm()

    return render(request, "accounts/guest_checkout.html", {"form": form})


# ------------------------
# Logout
# ------------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect("home")



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileFullEditForm
from .models import Profile

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile/profile.html', {"profile": profile})


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileFullEditForm(
            request.POST, request.FILES,
            instance=profile,
            user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileFullEditForm(
            instance=profile,
            user=request.user
        )

    return render(request, "profile/profile_edit.html", {"form": form})



