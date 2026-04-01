from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 🔹 Company Details
    company_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True)

    # 🔹 Contact Info
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # 🔹 System Flags
    is_vendor = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    # 🔥 TRUST SYSTEM (NEW)
    trust_score = models.IntegerField(default=100)

    def __str__(self):
        return self.company_name or self.user.username


# ===============================
# AUTO CREATE PROFILE
# ===============================
@receiver(post_save, sender=User)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created:
        VendorProfile.objects.create(user=instance)


# ===============================
# AUTO SAVE PROFILE
# ===============================
@receiver(post_save, sender=User)
def save_vendor_profile(sender, instance, **kwargs):
    if hasattr(instance, 'vendorprofile'):
        instance.vendorprofile.save()