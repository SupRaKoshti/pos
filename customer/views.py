from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from customer.models import Customer
from customer.serializers import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return super().create(request, *args, **kwargs)

class CustomerListView(viewsets.ViewSet):
    """
    View to list all customers.
    """
    def list(self, request):
        customers = Customer.objects.filter(is_active=True)
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    

class CustomerDetailView(viewsets.ViewSet):
    """
    View to retrieve a customer by ID.
    """
    def retrive(self, request, pk=None):
        try:
            customer = Customer.objects.get(pk=pk, is_active=True)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class CustomerUpdateView(viewsets.ViewSet):
    """
    View to update a customer by ID.
    """
    def update(self, request, pk=None):
        try:
            customer = Customer.objects.get(pk=pk, is_active=True)
            serializer = CustomerSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
        

class CustomerDeleteView(viewsets.ViewSet):
    """
    View to delete a customer by ID.
    """
    def destroy(self, request, pk=None):
        try:
            customer = Customer.objects.get(pk=pk, is_active=True)
            customer.is_active = False
            customer.save()
            return Response({'message':'Customer deleted successfully.'},status=status.HTTP_204_NO_CONTENT)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)