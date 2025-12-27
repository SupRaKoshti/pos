from django.shortcuts import render
from django.views import View

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


from .models import Tenant, TenantUser
from .serializers import TenantSerializer, TenantSignInSerializer

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

class TenantSignInView(APIView):
    """
    Public endpoint: Anyone can sign in.
    """
    permission_classes = [AllowAny]
    authentication_classes = [] 
    
    def post(self, request):
        serializer = TenantSignInSerializer(
            data=request.data,
            context={'request':request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = serializer.validated_data['tokens']
            
            tenant_user = serializer.validated_data['tenant_user']
            tenant = serializer.validated_data['tenant']


            return Response({
                'message':'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.get_full_name(),
                },
                'tenant':{
                    'id':tenant.id,
                    'business_name':tenant.business_name,
                    'is_verified':tenant.is_verified,
                    'subdomain':tenant.subdomain,
                },
                'tenant_user':{
                    'id':tenant_user.id
                },
                'tokens': tokens,
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )



