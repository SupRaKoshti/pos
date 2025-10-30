import re

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from customer.models import Customer

class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name field cannot be empty or whitespace")
        return value
    
    def validate_email(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Email field cannot ve empty or whitespace")
        
        queryset = Customer.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("Customer with this email already exists")    
        
        return value
    
    def validate_phone_number(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Phone number field cannot be empty or whitespace")
        
        cleaned = re.sub(r'[\s\-\(\)]','',value)

        if not re.match(r'^\+?\d{7,15}$',cleaned):
            raise serializers.ValidationError("Invalid phone number format")

        return value