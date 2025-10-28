from django.shortcuts import render

from rest_framework import viewsets

from inventory.models import ProductCategory, ProductSubCategory, Product, ProductVariant, InventoryItem
from inventory.seralizers import ProductCategorySerializer, ProductSubCategorySerializer, ProductSerializer, ProductVariantSerializer, InventoryItemSerializer

class ProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()

class ProductSubCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSubCategorySerializer
    queryset = ProductSubCategory.objects.all()

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

class ProductVariantViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVariantSerializer
    queryset = ProductVariant.objects.all()

class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    queryset = InventoryItem.objects.all()



