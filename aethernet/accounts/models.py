from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Automatically activate super admin
        if self.is_superuser:
            self.is_approved = True
        super().save(*args, **kwargs)

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)