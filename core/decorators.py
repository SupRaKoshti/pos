from functools import wraps

from rest_framework.response import Response
from rest_framework import status

from core.models import get_current_tenant

def require_feature(feature_name):
    """
    
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            tenant = get_current_tenant()

            if not tenant:
                return Response({
                    'error': 'no_tenant',
                    'message': 'No tenant context found.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not tenant.has_feature(feature_name):
                plan = tenant.subscription_plan
                return Response({
                    'error': 'feature_not_available',
                    'feature': feature_name,
                    'message': f"This feature is not available in your {plan.name} plan",
                    'current_plan': plan.name,
                    'upgrade_url': '/billing/upgrade/',
                    'required_plan': 'Professional or higher',
                }, status=status.HTTP_403_FORBIDDEN)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def check_resource_limit(resource_type):
    """
    Docstring for check_resource_limit
    
    :param resource_type: Description
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            tenant = get_current_tenant()

            if not tenant:
                return Response({
                    'error': 'no_tenant',
                    'message': 'No tenant context found.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            can_create = False

            if resource_type == 'products':
                can_create = tenant.can_add_product()
            elif resource_type == 'users':
                can_create = tenant.can_add_user()
            elif resource_type == 'transactions':
                can_create = tenant.can_access_transactions()

            if not can_create:
                plan = tenant.subscription_plan

                limits = {
                    'products': f"{tenant.current_product_count}/{plan.max_products}",
                    'users': f"{tenant.current_user_count}/{plan.max_users}",
                    'transactions': f"{tenant.current_monthly_transactions}/{plan.max_transactions_per_month}",
                }

                return Response({
                    'error': 'limit_exceeded',
                    'resource': resource_type,
                    'message': f"{resource_type.title()} limit reached",
                    'current': limits.get(resource_type, 'N/A'),
                    'current_plan': plan.name,
                    'upgrade_url': '/billing/upgrade/',
                }, status=status.HTTP_403_FORBIDDEN)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator