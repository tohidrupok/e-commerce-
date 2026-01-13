from django.db import models

class SiteHeadline(models.Model):
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class HomeSliderSection(models.Model):
    # Main slider (3)
    slider_1 = models.ImageField(upload_to='home_slider/')
    slider_2 = models.ImageField(upload_to='home_slider/')
    slider_3 = models.ImageField(upload_to='home_slider/')

    # Right side images (2)
    right_image_1 = models.ImageField(upload_to='home_slider/')
    right_image_2 = models.ImageField(upload_to='home_slider/')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Home Slider Section"


