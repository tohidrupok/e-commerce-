from django import forms

class CustomerRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class CustomerLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class GuestCheckoutForm(forms.Form):
    phone = forms.CharField(max_length=30)
    name = forms.CharField(max_length=150, required=False)  # optional
    email = forms.EmailField(required=False)


from django import forms
from .models import User, Profile

class ProfileFullEditForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['address', 'avatar']   # profile fields only

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # get request.user
        super().__init__(*args, **kwargs)

        # Pre-fill user fields
        self.user = user
        self.fields['username'].initial = user.username
        self.fields['email'].initial = user.email
        self.fields['phone'].initial = user.phone

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Update USER table
        self.user.username = self.cleaned_data['username']
        self.user.email = self.cleaned_data['email']
        self.user.phone = self.cleaned_data['phone']
        self.user.save()

        # Update PROFILE table
        if commit:
            profile.save()

        return profile

