from django.db import models
from threading import local

_thread_locals = local()

def get_current_tenant():
    """Get the current tenant from thread-local storage"""
    return getattr(_thread_locals, 'tenant', None)

def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage"""
    _thread_locals.tenant = tenant


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
    """
    Manager that returns only active records
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    

class BaseModel(models.Model):
    """
    Base model for all tenant-aware models
    Automatically adds tenant, timestamps, and soft delete
    """

    # Tenant field
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        db_index=True,
        help_text='Tenant this record belongs to'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete
    is_active = models.BooleanField(default=True)
    
    # Managers
    objects = TenantManager()
    all_objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        """Automatically set tenant on save if not already set"""
        if not self.tenant_id:
            tenant = get_current_tenant()
            if tenant:
                self.tenant = tenant
            else:
                raise ValueError(
                    f"Cannot save {self.__class__.__name__} without tenant context. "
                    "Ensure request goes through TenantMiddleware or set tenant manually."
                )
        super().save(*args, **kwargs)