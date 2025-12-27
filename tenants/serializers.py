from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Tenant, TenantUser
from account.models import CustomUser

class TenantSerializer(serializers.ModelSerializer):

    subscription_plan_name = serializers.CharField(
        source='subscription_plan.name',
        read_only=True
    )
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

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
            **validated_data
        )

        user = CustomUser.objects.create(
            email=validated_data['owner_email'],
            username=validated_data['owner_email'],
            phone=validated_data.get('phone', None)
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
    
class TenantSignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type':'password'}
    )

    def validate(self, data):
        """
        Validate the credintials and authenticate user
        """
        email = data.get('email')
        password = data.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                {"error":"Invalid email & password"}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"error":"Account is disabled"}
            )
        
        try:
            tenant_user = TenantUser.objects.select_related('tenant').get(user=user)
        except TenantUser.DoesNotExist:
            raise serializers.ValidationError(
                {"error":"No tenant associated with this user"}
            )
        
        if not tenant_user.is_active:
            raise serializers.ValidationError(
                {"error":"Account is disabled"}
        )
        
        tenant = tenant_user.tenant
        
        if not tenant.is_active:
            raise serializers.ValidationError(
                {"error":"Tenant is disabled"}
            )
        
        refresh = RefreshToken.for_user(user)
        refresh['tenant_id'] = str(tenant.id)
        refresh['tenant_subdomain'] = tenant.subdomain
        refresh['role'] = tenant_user.role

        data['user'] = user
        data['tenant_user'] = tenant_user
        data['tenant'] = tenant

        data['tokens'] = {
            'refresh':str(refresh),
            'access':str(refresh.access_token),
        }
        
        return data