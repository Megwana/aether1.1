from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def auto_approve_superuser(sender, instance, **kwargs):
    if instance.is_superuser and not instance.is_approved:
        instance.is_approved = True
        instance.save()
