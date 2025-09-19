from django.db import models
from core.models import BaseModel
from inventory.models import Product, ProductVariant

class Vendor(BaseModel):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True, unique=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.name
    
class VendorProduct(BaseModel):
    vendor = models.ForeignKey(Vendor, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='vendor_products', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='vendor_products', on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.IntegerField(default=0)
    min_order_quantity = models.IntegerField(default=1)
    max_order_quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('vendor', 'variant')

    def __str__(self):
        return f"{self.vendor.name} - {self.variant.variant_name}"
    
