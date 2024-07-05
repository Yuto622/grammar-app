from django.db import models


# Create your models here.
class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

