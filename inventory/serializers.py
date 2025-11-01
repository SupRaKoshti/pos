from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from inventory.models import ProductCategory, ProductSubCategory, Product, ProductVariant, InventoryItem

class ProductCategorySerializer(ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name field cannot be empty or whitespace.")
        return value

    def validate(self, data):
        name = data.get('name', None)
        queryset = ProductCategory.objects.filter(name=name)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("ProductCategory with this name already exists")
        return data
        
class ProductSubCategorySerializer(ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProductSubCategory
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name field cannot be empty or whitespace.")
        return value

    def validate(self,data):
        name = data.get('name', None)
        category = data.get('category',None)

        queryset = ProductSubCategory.objects.filter(name=name)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exist():
            raise serializers.ValidationError("ProductSubCategory with this name already exists")
        
        if not ProductCategory.objects.filter(id=category.id).exists():
            raise serializers.ValidationError("Product Category with this name is not exists")
        return data

class ProductSerializer(ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name field cannot be empty or whitespace.")
        return value
    
    def validate(self,data):
        name = data.get('name', None)
        subcategory = data.get('subcategory',None)
        if Product.objects.filter(name=name).exists():
            raise serializers.ValidationError("Product with this name already exists")
        if not ProductSubCategory.objects.filter(id=subcategory.id).exists():
            raise serializers.ValidationError("Product SubCategory with this name is not exists")
        return data
        
class ProductVariantSerializer(ModelSerializer):

    class Meta:
        model = ProductVariant
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name field cannot be empty or whitespace.")
        return value
    
    def validate(self,data):
        sku = data.get('sku', None)
        queryset = ProductVariant.objects.filter(sku=sku)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("Product Variant with this SKU already exists")
        
        price = data.get('price', None)
        if price is not None and price <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        
        return data

class InventoryItemSerializer(ModelSerializer):
    expired_date = serializers.DateField(required=False, allow_null=True)
    batch_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = InventoryItem
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name field cannot be empty or whitespace.")
        return value
    
    def validate(self,data):
        item_code = data.get('item_code', None)
        queryset = InventoryItem.objects.filter(item_code=item_code)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("Inventory Item with this item code already exists")
        
        expired_date = data.get('expired_date', None)
        if expired_date and not self.instance:
            from datetime import date
            if expired_date <= date.today():
                raise serializers.ValidationError("Expired date must be a future date.")
        
        return data