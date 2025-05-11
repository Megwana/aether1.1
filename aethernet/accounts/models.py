from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Automatically activate super admin
        if self.is_superuser:
            self.is_approved = True
        super().save(*args, **kwargs)

