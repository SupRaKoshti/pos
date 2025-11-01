import uuid

from django.db import models

from core.models import BaseModel
from customer.models import Customer
from inventory.models import Product
# Create your models here.

class Sale(BaseModel):
    sale_id = models.CharField(max_length=100, unique=True)
    customer_name = models.ForeignKey(
        Customer, on_delete=models.DO_NOTHING
    )
    invoice = models.CharField(max_length=100)
    date = models.DateField()
    items_quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def save(self, *args, **kwargs):
        if not self.sale_id:
            unique_code = uuid.uuid4().hex[:6].upper()
            date_str = self.date.strftime('%Y%m%d') if self.date else ''
            self.sale_id = f"SALE-{date_str}-{unique_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.sale_id
    
class SaleItem(BaseModel):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.sale.sale_id} - {self.product_name.name}"