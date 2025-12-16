from django.http import Http404, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from tenants.models import Tenant
from core.models import set_current_tenant, get_current_tenant

class TenantMiddleware(MiddlewareMixin):
    """
    Middlware to identify and set the current tenant based on subdomain

    How it works:
    1. Extract subdomain from request (e.g., 'starbucks' from 'starbucks.yourpos.com')
    2. Look up tenant in database by subdomain
    3. Store tenant in thread-local storage for the request
    4. All subsequent queries are automatically filtered by this tenant
    """

    SKIP_SUBDOMAINS = ['www', 'admin', 'api', 'static', 'media']

    PUBLIC_URLS = [
        '/admin/',
        '/account/api/login/',
        '/tenant/signup/',
        '/account/api/register/'
        '/api/health/',
        '/static/',
        '/media/',
    ]

    def process_request(self, request):
        """Process incoming request and set tenant"""

        if any(request.path.startswith(url) for url in self.PUBLIC_URLS):
            set_current_tenant(None)
            return None
        
        hostname = request.get_host().split(':')[0] # Remove port

        subdomain = self.get_subdomain(hostname) # Extract subdomain

        if not subdomain or subdomain in self.SKIP_SUBDOMAINS:
            set_current_tenant(None)
            return None
        
        try:
            tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)

            if not tenant.is_subscription_active():
                return JsonResponse({
                    'error':'Subscription expired',
                    'message':f'Your subscription has expired. Please contact support.',
                    'tenant':tenant.business_name,
                    'days_until_expiry':tenant.days_until_expiry()
                }, status=403)
            
            # Set tenant for this request
            set_current_tenant(tenant)
            request.tenant = tenant 

        except Tenant.DoesNotExist:
            return JsonResponse({
                'error':'Tenant not found',
                'message':f"No business found with subdomain '{subdomain}'",
                'subdomain':subdomain
            }, status=404)
            pass
        return None
    
    def get_subdomain(self, hostname):
        """
        Extract subdomain from hostname

        Examples:
        - 'starbucks.yourpos.com' → 'starbucks'
        - 'starbucks.localhost' → 'starbucks'
        - 'yourpos.com' → None
        - 'localhost' → None
        """

        parts = hostname.split('.')

        # Handle localhost
        if hostname == 'localhost' or hostname == '127.0.0.1':
            return None
        
        # Handle *.localhost (e.g., starbucks.localhost)
        if len(parts) >=2 and parts[-1] == 'localhost':
            return parts[0]
        
        # Handle regular domains (e.g., starbucks.yourpos.com)
        if len(parts) >= 3:
            return parts[0]
        
        # No subdomain
        return None 
        
      
    def process_response(self, request, response):
        """Clean up tenant from thread-local storage after request"""
        set_current_tenant(None)
        return response
    
    def process_exception(self, request, exception):
        """Clean up on exception"""
        set_current_tenant(None)
        return None