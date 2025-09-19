from django.db import models
from core.models import BaseModel

class Customer(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    loyalty_points_achieved = models.IntegerField(default=0)
    loyalty_points_redeemed = models.IntegerField(default=0)

    @property
    def loyalty_points_balance(self):
        return self.loyalty_points_achieved - self.loyalty_points_redeemed