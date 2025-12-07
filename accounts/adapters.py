from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # allow standard signup
        return True

class CustomSocialAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # allow social signup (but we'll force role below)
        return True

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Ensure all social-created users are customers and have no admin rights
        user.role = "customer"
        # Do not set staff/superuser flags for social signup
        user.is_staff = False
        user.is_superuser = False
        # If provider gave phone number, try to set it (may vary by provider scopes)
        phone = sociallogin.account.extra_data.get("phone") if sociallogin.account.extra_data else None
        if phone:
            user.phone = phone
        user.save()
        return user
