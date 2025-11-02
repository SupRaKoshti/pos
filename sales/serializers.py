from django.db.models import Sum

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from customer.models import Customer
from inventory.models import Product
from sales.models import Sale, SaleItem
from customer.serializers import CustomerSerializer
from inventory.serializers import ProductSerializer

class SaleItemSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_id', 'sale', 'quantity', 'unit_price', 'total_price']

    def validate_product(self, value):
        stock = value.variants.first().inventory_items.aggregate(total_stock=Sum('quantity_in_stock'))['total_stack'] or 0
        if stock < self.initial_data.get('quantity', 0):
            raise serializers.ValidationError(f"Insufficient stock for product {value.name}. Available stock: {stock}")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value

    def validate(self, data):
        unit_price = data.get('unit_price')
        quantity = data.get('quantity')
        total_price = unit_price * quantity

        if data['total_price'] < total_price:
            raise serializers.ValidationError("Total price does not match unit price multiplied by quantity.")
        
        return data

    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data['quantity']
        unit_price = validated_data['unit_price']
        total_price = quantity * unit_price
        
        inventory_item = product.variants.first().inventory_items.first()
        
        if inventory_item:
            if inventory_item.quantity_in_stock < quantity:
                raise serializers.ValidationError(f"Insufficient stock for product {product.name}.")
            
            sale_item = SaleItem.objects.create(
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                **{k: v for k, v in validated_data.items() if k not in ['product', 'quantity', 'unit_price']}
            )

            inventory_item.quantity_in_stock -= quantity
            inventory_item.save()
            sale_item.save()
            return sale_item
        else:
            raise serializers.ValidationError(f"No inventory item found for product {product.name}.")
        

class SaleSerializer(ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source='customer', write_only=True)
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ['id', 'customer', 'customer_id', 'invoice', 'date', 'items_quantity', 'total_amount', 'payment_method', 'notes', 'discount', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)

        total_amount = 0
        total_quantity = 0

        for item_data in items_data:
            item_data['sale'] = sale
            sale_item_serializer = SaleItemSerializer(data=item_data)
            sale_item_serializer.is_valid(raise_exception=True)
            sale_item = sale_item_serializer.save()
            total_amount += sale_item.total_price
            total_quantity += sale_item.quantity
            sale.total_amount = total_amount - sale.discount
            sale.items_quantity = total_quantity
            sale.save()

        return sale
    
    def validate_discount(self, value):
        if value < 0:
            raise serializers.ValidationError("Discount cannot be negative.")
        return value
    
    def validate(self, data):
        total_amount = data.get('total_amount', 0)
        discount = data.get('discount', 0)
        if discount > total_amount:
            raise serializers.ValidationError("Discount cannot be greater than total amount.")
        return data
    
    