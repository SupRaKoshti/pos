from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from core.models import BaseModel


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?[0-9]{10,15}$',
        message="Enter a valid phone number"
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=17,validators=[phone_regex], blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    
class UserProfile(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


