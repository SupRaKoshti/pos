from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from core.models import set_current_tenant, get_current_tenant
from tenants.models import Tenant, SubscriptionPlan
from inventory.models import Product, ProductCategory

User = get_user_model()

class TenantIsolationTestCase(TestCase):
    """Critical security tests for tenant isolation"""

    def setUp(self):
        # create the test subscription plan
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            plan_type="trial",
            max_users=10,
            max_products=1000
        )

        # create test tenant A 
        self.tenant_a = Tenant.objects.create(
            business_name="Test Business A",
            subdomain="tenant-a",
            owner_name="Owner A",
            owner_email="a@test.com",
            subscription_plan=self.plan,
            subscription_status='active'
        )

        # create test tenant B
        self.tenant_b = Tenant.objects.create(
            business_name="Test Business B",
            subdomain='tenant-b',
            owner_name="Owner B",
            owner_email="b@test.com",
            subscription_plan=self.plan,
            subscription_status='active'
        )

        set_current_tenant(self.tenant_a)
        self.cat_a = ProductCategory.objects.create(name="Category A")

        set_current_tenant(self.tenant_b)
        self.cat_b = ProductCategory.objects.create(name="Category B")

        set_current_tenant(None)

    def test_tenant_isolation(self):
        """Test basic tenant isolation"""
        set_current_tenant(self.tenant_a)
        categories = ProductCategory.objects.all()

        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().name, "Category A")

    def test_cross_tenant_access_denied(self):
        """Test that accessing other tenant's data by ID fails"""
        set_current_tenant(self.tenant_a)

        with self.assertRaises(ProductCategory.DoesNotExist):
            ProductCategory.objects.get(id=self.cat_b.id)

    def test_admin_bypass(self):
        """Test that all_objects bypasses tenant filter"""
        set_current_tenant(self.tenant_a)

        all_categories = ProductCategory.all_objects.all()

        self.assertEqual(all_categories.count(), 2)

    def tearDown(self):
        set_current_tenant(None)