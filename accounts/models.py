from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    is_vendor = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name


@receiver(post_save, sender=User)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created:
        VendorProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_vendor_profile(sender, instance, **kwargs):
    instance.vendorprofile.save()

@receiver(post_save, sender=User)
def save_vendor_profile(sender, instance, **kwargs):
    instance.vendorprofile.save()