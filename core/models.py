from django.db import models


class TenantManager(models.Manager):
    """
    custom manager that automatically filters all queries by current tenant
    This ensures data isolation across tenants.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = get_current_tenant()

        if tenant is not None:
            return queryset.filter(tenant=tenant)
        return queryset


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True
        ordering = ['created_at']

