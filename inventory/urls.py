from django.urls import path, include
from inventory.views import (
    ProductCategoryViewSet,
    ProductSubCategoryViewSet,
    ProductViewSet,
    ProductVariantViewSet,
    InventoryItemViewSet,
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'product-categories', ProductCategoryViewSet, basename='productcategory')
router.register(r'product-subcategories', ProductSubCategoryViewSet, basename='productsubcategory')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-variants', ProductVariantViewSet, basename='productvariant')
router.register(r'inventory-items', InventoryItemViewSet, basename='inventoryitem')

urlpatterns = [
    path("", include(router.urls)),
]