from django.utils.text import slugify
from django.utils import timezone

from rest_framework import serializers, ModelSerializer

from .models import Tenant, TenantUser
from account.models import CustomUser

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
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        
        business_name = validated_data['business_name']
        base_subdomain = slugify(business_name)[:50]

        subdomain = base_subdomain
        counter = 1

        while Tenant.objects.filter(subdomain=subdomain).exists():
            subdomain = f"{subdomain}-{counter}"
            counter += 1
            
            if len(subdomain) > 63:
                subdomain = base_subdomain[:59 - len(str(counter))] + f"{counter}"

        validated_data['subdomain'] = subdomain

        tenant = Tenant.objects.create(
            subdomain=subdomain,
            **validated_data
        )

        user = CustomUser.objects.create(
            email=validated_data['owner_email'],
            username=validated_data['owner_email'],
            phone=validated_data['phone'] if validated_data['phone'] else None,
        )
        user.set_password(password)
        user.save()

        TenantUser.objects.create(
            user=user,
            tenant=tenant,
            role='owner',
            is_active=True
        )

        return tenant