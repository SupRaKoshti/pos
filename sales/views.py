from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from sales.models import Sale
from sales.serializers import SaleSerializer, SaleItemSerializer
from inventory.models import Product
from inventory.serializers import ProductSerializer

class SaleAPIView(APIView):
    def get(self, request):
        sales = Sale.objects.prefetch_related('items').all()
        serializer = SaleSerializer(sales, many=True)
        return Response(serializer, status=status.HTTP_200_OK)
    
    def post(self, request):
        sale_serializer = SaleSerializer(data=request.data)
        if sale_serializer.is_valid():
            sale = sale_serializer.save()
            return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)
        return Response(sale_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def handle_update(self, request, sale_id, partial=False):
        try:
            sale = Sale.objects.get(sale_id=sale_id)
        except Sale.DoesNotExist:
            return Response({"error": "Sale not found."}, status=status.HTTP_404_NOT_FOUND)
        
        sale_serializer = SaleSerializer(sale, data=request.data, partial=partial)

        if sale_serializer.is_valid():
            sale_serializer.save()
            return Response(SaleSerializer(sale).data, status=status.HTTP_200_OK)
        return Response(sale_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, sale_id):
        return self.handle_update(request, sale_id)
    
    def patch(self, request, sale_id):
        return self.handle_update(request, sale_id, partial=True)
    
    def delete(self, request, sale_id):
        try:
            sale = Sale.objects.get(sale_id=sale_id)
            sale.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Sale.DoesNotExist:
            return Response({"error": "Sale not found."}, status=status.HTTP_404_NOT_FOUND)
        
    
    