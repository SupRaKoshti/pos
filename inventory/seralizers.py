from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from inventory.models import ProductCategory, ProductSubCategory, Product, ProductVariant, InventoryItem

class ProductCategorySerializer(ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'

    def validate(self, data):
        name = data.get('name', None)
        if ProductCategory.objects.filter(name=name).exists():
            raise ModelSerializer.ValidationError("Product Category with this name already exists.")        
        return data
        
class ProductSubCategorySerializer(ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProductSubCategory
        fields = '__all__'

    def validate(self,data):
        name = data.get('name', None)
        category = data.get('category',None)
        if ProductSubCategory.objects.filter(name=name).exists():
            raise ModelSerializer.ValidationError("ProductSubCategory with this name already exists")
        if not ProductCategory.objects.filter(id=category.id).exists():
            raise ModelSerializer.ValidationError("Product Category with this name is not exists")
        return data

class ProductSerializer(ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = '__all__'

    def validate(self,data):
        name = data.get('name', None)
        subcategory = data.get('subcategory',None)
        if Product.objects.filter(name=name).exists():
            raise ModelSerializer.ValidationError("Product with this name already exists")
        if not ProductSubCategory.objects.filter(id=subcategory.id).exist():
            raise ModelSerializer.ValidationError("Product SubCategory with this name is not exists")
        return data
        
class ProductVariantSerializer(ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

        def validate(self,data):
            sku = data.get('sku', None)
            if ProductVariant.objects.filter(sku=sku).exists():
                raise ModelSerializer.ValidationError("Product Variant with this SKU already exists")
            return data

class InventoryItemSerializer(ModelSerializer):
    expired_date = serializers.DateField(required=False, allow_null=True)
    batch_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = InventoryItem
        fields = '__all__'

        def validate(self,data):
            item_code = data.get('item_code', None)
            if InventoryItem.objects.filter(item_code=item_code).exists():
                raise ModelSerializer.ValidationError("Inventory Item with this item code already exists")
            return data