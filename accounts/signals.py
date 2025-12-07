from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile

@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, phone=instance.phone or "")

@receiver(post_save, sender=User)
def save_profile_for_user(sender, instance, **kwargs):
    # ensure profile exists and keep phone in sync if provided
    if hasattr(instance, "profile"):
        if instance.phone and instance.profile.phone != instance.phone:
            instance.profile.phone = instance.phone
            instance.profile.save()
    else:
        Profile.objects.create(user=instance, phone=instance.phone or "")
