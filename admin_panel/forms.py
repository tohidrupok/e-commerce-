from django import forms
from .models import HomeSliderSection

class HomeSliderSectionForm(forms.ModelForm):
    class Meta:
        model = HomeSliderSection
        fields = '__all__'
