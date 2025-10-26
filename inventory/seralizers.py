from rest_framework.serializers import ModelSerializer
from inventory.models import ProductCategory, ProductSubCategory, Product, ProductVariant, InventoryItem

class ProductCategorySerializer(ModelSerializer):
    description = ModelSerializer.CharField(required=False, allow_blank=True)
    image = ModelSerializer.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProductCategory
        fields = '__all__'

    def validate(self, data):
        name = data.get('name', None)
        if ProductCategory.objects.filter(name=name).exists():
            raise ModelSerializer.ValidationError("Product Category with this name already exists.")        
        return data
        
class ProductSubCategorySerializer(ModelSerializer):
    description = ModelSerializer.CharField(required=False, allow_blank=True)
    image = ModelSerializer.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProductSubCategory
        fields = '__all__'

    def validate(self,data):
        name = data.get('name', None)
        category = data.get('category',None)
        if ProductSubCategory.objects.filter(name=name).exists():
            raise ModelSerializer.ValidationError("ProductSubCategory with this name already exists")
        if ProductCategory.objects.exclude(category=category).exits():
            raise ModelSerializer.ValidationError("Product Category with this name is not exists")
        return data