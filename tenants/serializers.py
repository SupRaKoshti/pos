from django.utils.text import slugify

from rest_framework import serializers, ModelSerializer

from .models import Tenant

class TenantSerializer(ModelSerializer):

    subscription_plan_name = serializers.CharField(
        source='subscription_plan.name',
        read_only=True
    )

    class Meta:
        model = Tenant
        fields = '__all__'
        read_only_fields = (
            'id',
            'subdomain',
            'created_at',
            'updated_at',
            'trial_starts_at',
            'trial_ends_at',
            'subscription_status',
            'subscription_starts_at',
            'subscription_ends_at',
            'last_payment_date',
            'next_billing_date',
            'current_users_count',
            'current_product_count',
            'current_month_transactions',
            'is_active',
            'is_verified',
            'subscription_plan_name',
        )

    def validate_owner_email(self, value):
        if self.instance:
            if Tenant.objects.filter(owner_email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Tenant with this email already exists.")
        else:
            if Tenant.objects.filter(owner_email=value).exists():
                raise serializers.ValidationError("Tenant with this email already exists.")
        return value
    
    def validate_subdomain(self, value):
        if Tenant.objects.filter(subdomain=value).exists():
            raise serializers.ValidationError("Tenant with this domain already exists.")
        
        RESERVED_SUBDOMAINS = ['www', 'admin', 'api', 'mail', 'ftp', 'dashboard']
        if value.lower() in RESERVED_SUBDOMAINS:
            raise serializers.ValidationError("This subdomain is reserved and cannot be used.")
        
        return value
        
    def create(self, validated_data):
        business_name = validated_data['business_name']
        base_subdomain = slugify(business_name)[:50]

        subdomain = base_subdomain
        counter = 1

        while Tenant.objects.filter(subdomain=subdomain).exists():
            subdomain = f"{subdomain}-{counter}"
            counter += 1
            
