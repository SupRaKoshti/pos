from django.shortcuts import render
from django.views import View

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


from .models import Tenant
from .serializers import TenantSerializer

class TenantSignUpView(generics.CreateAPIView):
    """
    Public endpoint: Anyone can sign up to create a new tenant.
    """
    serializer_class = TenantSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = TenantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()

        return Response({
            "message": "Tenant created successfully.",
            "tenant": serializer.data
        }, status=status.HTTP_201_CREATED)

