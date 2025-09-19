from django.db import models
from core.models import BaseModel

class ProductCategory(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class ProductSubCategory(BaseModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ProductCategory, related_name='subcategories', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
class Product(BaseModel):
    name = models.CharField(max_length=255)
    subcategory = models.ForeignKey(ProductSubCategory, related_name='products', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class InventoryItem(BaseModel):
    item_code = models.CharField(max_length=100, unique=True)
    variant = models.ForeignKey(ProductVariant, related_name='inventory_items', on_delete=models.CASCADE)
    
    quantity_in_stock = models.IntegerField(default=0)
    expired_date = models.DateField(blank=True, null=True)

    batch_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.item_code} - {self.variant.variant_name}"
    



