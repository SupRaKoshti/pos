from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from inventory.models import Product
from sales.models import Sale, SaleItem
from customer.serializers import CustomerSerializer
from inventory.serializers import ProductSerializer

class SaleItemSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_id','sale', 'quantity', 'unit_price', 'total_price']

    

