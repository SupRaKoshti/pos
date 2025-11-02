from django.urls import path, include

from sales.views import SaleAPIView

urlpatterns = [
    path('list/', SaleAPIView.as_view(), name='sales_api'),
    path('<str:sale_id>/', SaleAPIView.as_view(), name='sale_detail_api'),
]