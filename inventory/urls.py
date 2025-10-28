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

urlpatterns = [
    path("", include(router.urls)),
]