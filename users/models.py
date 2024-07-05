from django.db import models
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def clean(self):
        # Custom validation for username
        if self.username and self.username.lower() == 'admin':
            raise ValidationError('Username "admin" is not allowed.')

        # Custom validation for password length
        if self.password and len(self.password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')

    def save(self, *args, **kwargs):
        # Call full_clean to ensure all validations are applied before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
