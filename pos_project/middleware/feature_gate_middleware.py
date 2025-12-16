from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from core.models import get_current_tenant
from tenants.models import UsageTracking
from datetime import datetime

class FeatureGateMiddleware(MiddlewareMixin):
    """
    Enforce subscription plan limits and feature access
    Checks BEFORE processing each request
    """
    
    EXEMPT_URLS = [
        '/admin/',
        '/tenant/signup/',
        '/api/login/',
        '/api/logout/',
        '/billing/upgrade/',
        '/static/',
        '/media/',
    ]

    LIMIT_CHCEKS = {
        '/api/users/':'users',
        '/api/products/':'products',
        '/api/sales/':'transactions',
    }

    def process_request(self, request):
        """Check limits before processing request"""

        if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            return None
        
        tenant = get_current_tenant()

        if not tenant:
            return None
        
        if not tenant.is_subscription_active:
            subscription = tenant.subscription_details

            if subscription.is_in_grace_period:
                response = self.get_response(request)
                response['X-Subscription-Grace-Period'] = 'true'
                return response
            else:
                return JsonResponse({
                    'error': 'subscription_expired',
                    'message': 'Your subscription has expired. Please renew to continue using the service.',
                    'days_overdue': abs(subscription.days_remaining()),
                    'upgrade_url': '/billing/upgrade/',
                }, status=402)
        
        if request.method == 'POST':
            for url_pattern, resource_type in self.LIMIT_CHECKS.items():
                if request.path.startswith(url_pattern):
                    can_create, message = self._check_resource_limit(tenant, resource_type)

                    if not can_create:
                        return JsonResponse({
                            'error': 'limit_exceeded',
                            'resource': resource_type,
                            'message': message,
                            'current_plan': tenant.subscription_details.plan_name,
                            'upgrade_url': '/billing/upgrade/',
                        }, status=403)
                    
        return None
    
    def _check_resource_limit(self, tenant, resource_type):
        """Check if tenant can create more of the given resource type"""

        usage = self._get_current_usage(tenant)
        plan = tenant.subscription_plan

        if resource_type == 'users':
            current = usage.active_users_count if usage else 0
            limit = plan.max_users

            if current >= limit:
                return False, f"User limit reached ({current}/{limit}). Upgrade your plan to add more users."
        
        elif resource_type == 'products':
            current = usage.products_count if usage else 0
            limit = plan.max_products

            if current >= limit:
                return False, f"Product limit reached ({current}/{limit}). Upgrade your plan to add more products."
            
        elif resource_type == 'transactions':
            current = usage.transactions_count if usage else 0
            limit = plan.max_transactions_per_month

            if current >= limit:
                return False, f"Monthly transaction limit reached ({current}/{limit}). Upgrade to increase your limit."
        
        return True,"Within limits"
    
    def _get_current_usage(self, tenant):
        """Get or create current month usage tracking"""

        now = datetime.now()

        usage, created = UsageTracking.objects.get_or_create(
            tenant=tenant,
            period_month=now.month,
            period_year=now.year,
            defaults={
                'period_start': now.date(),
                'period_end': now.date(),
            }
        )

        return usage
    
    def process_response(self, request, response):
        """Add usage info to response headers"""
        tenant = get_current_tenant()

        if tenant and hasattr(response, 'status_code') and response.status_code < 400:
            usage = self._get_current_usage(tenant)
            plan = tenant.subscription_plan

            response['X-Plan'] = plan.name
            response['X-Users-Limit'] = f"{usage.active_users_count}/{plan.max_users}"
            response['X-Products-Limit'] = f"{usage.products_count}/{plan.max_products}"
            response['X-Transactions-Limit'] = f"{usage.transactions_count}/{plan.max_transactions_per_month}"

        return response