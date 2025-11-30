from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import timedelta, date
import uuid

class SubscriptionPlan(models.Model):
    """
    Different subscription tiers for your POS system
    Example: Free Trial, Basic, Professional, Enterprise
    """

    PLAN_TYPES = [
        ('trial','Free Trial'),
        ('basic','Basic Plan'),
        ('professional','Professional Plan'),
        ('enterprise','Enterprise Plan')
    ]

    # Basic Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    plan_type = models.CharField(max_length=50, choices=PLAN_TYPES, default='trial')
    description = models.TextField(blank=True)

    # Pricing
    price_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Monthly subscription price'
    )
    price_yearly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Yearly subscription price (Usually with discount)'
    )

    # Feature Limits
    max_users = models.IntegerField(
        default=1,
        help_text='Maximum User/Staff allowed'
    )
    max_products = models.IntegerField(
        default=100,
        help_text='Maximum products in inventory'
    )
    max_transactions_per_month = models.IntegerField(
        default=100,
        help_text='Maximum sales transactions per month'
    )
    max_locations = models.IntegerField(
       default=1,
       help_text='Maximum store locations' 
    )

    # Features (Boolean Flags)
    has_analytics = models.BooleanField(default=False)
    has_advanced_reports = models.BooleanField(default=False)
    has_multi_location = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    has_custom_branding = models.BooleanField(default=False)
    has_inventory_alerts = models.BooleanField(default=True)
    has_customer_management = models.BooleanField(default=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(
        default=True,
        help_text='Show in pricing page'
    )
    sort_order = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order','price_monthly']
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} - ₹{self.price_monthly}/month"
    
    def get_yearly_discount_percent(self):
        """Calculate discount percentange for yearly plan"""
        if self.price_monthly > 0 and self.price_yearly > 0:
            yearly_if_monthly = self.price_monthly * 12
            discount = ((yearly_if_monthly - self.price_yearly)/yearly_if_monthly)
            return round(discount,1)
        return 0
    

class Tenant(models.Model):
    """
    Represents a business/company using your POS system
    Each tenant is completely isolated from others
    """

    SUBSCRIPTION_STATUS = [
        ('trial','Trial Period'),
        ('active','Active'),
        ('past_due','Past Due'),
        ('expired','Expired'),
        ('cancelled','Cancelled'),
        ('suspended','Suspended'),
    ]

    BILLING_CYCLE = [
        ('monthly','Monthly'),
        ('yearly','Yearly'),
    ]

    # Basic Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    business_name = models.CharField(
        max_length=200,
        help_text='Legal business/company name'
    )

    subdomain = models.SlugField(
        max_length=63,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$',
                message='Subdomain must be lowercase letters, numbers, and hypens only'
            )
        ]
    )

    # Contact Information
    owner_name = models.CharField(max_length=200)
    owner_email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    # Business Information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='India')

    # Tax Information (for billing)
    gstin = models.CharField(
        max_length=50,
        blank=True,
        help_text='GST Identification Number (India)'
    )

    # Subscription Management
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='tenants'
    )

    subscription_status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS,
        default='trial'
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE,
        default='monthly'
    )

    # Important Dates
    created_at = models.DateTimeField(auto_now_add=True)
    trial_starts_at = models.DateTimeField(default=timezone.now)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_starts_at = models.DateTimeField(null=True, blank=True)
    subscription_ends_at = models.DateTimeField(null=True, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)

    # Setting
    timezone = models.CharField(max_length=50, default='Asis/Kolkata')
    currency = models.CharField(max_length=3, default='INR')
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY')

    # Feature Overrides (JSON for custom features per tenant)
    custom_features = models.JSONField(
        default=dict,
        blank=True,
        help_text='Custom feature flags that override plan defaults'
    )

    # Usage Tracking
    current_users_count = models.IntegerField(default=0)
    current_product_count = models.IntegerField(default=0)
    current_month_transactions = models.IntegerField(default=0)

    # Status & Metadata
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['owner_email']),
            models.Index(fields=['subscription_status', 'is_active']),
        ]
        verbose_name = 'Tenant'
        verbose_name_plural = "Tenants"

    def __str__(self):
        return f"{self.business_name} ({self.subdomain})"
    
    def save(self, *args, **kwargs):
        """Set trial end date on creation"""
        if not self.pk:
            if not self.trial_ends_at:
                # 14-days trial period
                self.trial_ends_at = timezone.now() + timedelta(days=14)
            if not self.subscription_ends_at:
                self.subscription_ends_at = self.trial_ends_at

        self.subdomain = self.subdomain.lower()

        super().save(*args, **kwargs)

    def is_subscription_active(self):
        """Check if tenant's subscription is currently active"""
        if not self.is_active:
            return False
        
        now = timezone.now()

        # Check trial period
        if self.subscription_status == 'trial':
            return now <= self.trial_ends_at
        
        # Check active subscription
        if self.subscription_status == 'active':
            if self.subscription_ends_at:
                return now <= self.subscription_ends_at
            return True
    
        return False

    def days_until_expiry(self):
        """Calculate days remaining in subscription"""

        if not self.is_subscription_active():
            return 0
        
        now = timezone.now()

        if self.subscription_status == 'trial':
            delta = self.trial_ends_at - now
        elif self.subscription_ends_at:
            delta = self.subscription_ends_at - now
        else:
            return None
        
        return max(0, delta.days)
    
    def is_trial(self):
        """Check if tenant is in trial period"""
        return self.subscription_status == 'trial' and self.is_subscription_active()
    
    def has_feature(self, feature_name):
        """
        Check if tenant has access to a specific feature
        Checks custom overrides first, then plan features
        """

        if feature_name in self.custom_features:
            return self.custom_features[feature_name]

        # Check plan features    
        feature_attr = f"has_{feature_name}"
        return getattr(self.subscription_plan, feature_attr, False)
    
    def is_within_limits(self):
        """Check if tenant is within their plan limits"""
        issues = []

        # Check user limit
        if self.current_users_count > self.subscription_plan.max_users:
            issues.append(f"User limit exceeded ({self.current_users_count}/{self.subscription_plan.max_users})")

        # Check product limit
        if self.current_product_count > self.subscription_plan.max_products:
            issues.append(f"Product limit exceeded ({self.current_product_count}/{self.subscription_plan.max_products})")

        # Check transaction limit
        if self.current_month_transactions > self.subscription_plan.max_transactions_per_month:
            issues.append(f"Monthly transaction limit exceeded ({self.current_month_transactions}/{self.subscription_plan.max_transactions_per_month})")

        return (len(issues) == 0,issues)
    
    def can_add_user(self):
        """Check if tenant can add more users"""
        return self.current_users_count < self.subscription_plan.max_users
    
    def can_add_product(self):
        """Check if tenant can add more products"""
        return self.current_product_count < self.subscription_plan.max_products
    
    def can_process_transaction(self):
        """Check if tenant can process more transaction this month"""
        return self.current_month_transactions < self.subscription_plan.max_transactions_per_month
    
    # =========================================================
    # Plan Management Methods
    # =========================================================

    def upgrade_plan(self, new_plan, billing_cycle='monthly'):
        """Upgrade to a different subscription plan"""
        old_plan = self.subscription_plan
        self.subscription_plan = new_plan
        self.billing_cycle = billing_cycle

        # Update status
        if self.subscription_status == 'trial':
            self.subscription_status = 'active'
            self.subscription_starts_at = timezone.now()

        # Calculate new subscription end date
        if billing_cycle == 'monthly':
            self.subscription_ends_at = timezone.now() + timedelta(days=30)
        else:
            self.subscription_ends_at = timezone.now() + timedelta(days=365)

        # Set next billing date
        self.next_billing_date = self.subscription_ends_at

        self.save()

        # Log the upgrade (you can create a TenantHistory model for this)
        return {
            'successs':True,
            'message':f'Upgraded from {old_plan.name} to {new_plan.name}',
            'old_plan':old_plan.name,
            'new_plan':new_plan.name,
        }
    
    def cancel_subscription(self):
        """Cancel subscription (keeps active until end date)"""
        self.subscription_status = 'cancelled'
        self.note += f"\nCancelled on {timezone.now()}"
        self.save()

    def suspend(self, reason=""):
        """Immediately suspend tenant (e.g., payment failure, violation)"""
        self.subscription_status = 'suspended'
        self.is_active = False
        if reason:
            self.notes += f"\nSuspended on {timezone.now()}: {reason}"
        self.save()
    
    def reactivate(self):
        """Reactivate a suspended/cancelled tenant"""
        self.subscription_status = 'active'
        self.is_active = True
        self.notes += f"\nReactivated on {timezone.now()}"
        self.save()


class TenantUser(models.Model):
    """
    Links Django User to Tenants with roles
    Allows users to belong to multiple tenants (e.g.,consultant managing multiple stores)
    """

    ROLES = [
        ('owner','Owner'),
        ('admin','Administrator'),
        ('manager','Manager'),
        ('cashier','Cashier'),
        ('staff','Staff')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
        related_name='tenant_memberships'
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='user_memberships'
    )

    role = models.CharField(max_length=20, choices=ROLES, default='staff')

    # Permissions (JSON for granular permissions)
    permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom permissions : {'can_delete_sales':True, 'can_view_reports':True}"
    )

    # Invitation tracking
    invited_by = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_tenant_users'
    )
    invited_sent_at = models.DateTimeField(null=True, blank=True)
    invited_accepted_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user','tenant']]
        ordering = ['-joined_at']
        verbose_name = 'Tenant User'
        verbose_name_plural = 'Tenant Users'

    def __str__(self):
        return f"{self.user.email} - {self.tenant.business_name} ({self.role})"
    
    def has_permission(self, persmission_name):
        """Check if user has a specific permission in this tenant"""
        if self.role in ['owner','admin']:
            return True

        return self.permissions.get(persmission_name, False)
    
    def can_manage_subscription(self):
        """Only owners can manage subscription"""
        return self.role == 'owner'
    

class Subscription(models.Model):
    """
    Detailed subscription tracking for each tenant
    Separates subscription logic from Tenant model
    """

    STATUS_CHOICES = [
        ('trial', 'Trial Period'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to tenant
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='subscription_detail'
    )

    # Current plan
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='active_subscriptions'
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')

    # Trial period
    trial_starts_at = models.DateTimeField(default=timezone.now)
    trial_ends_at = models.DateTimeField()

    # Billing cycle
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()

    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    # Auto-renewal
    auto_renew = models.BooleanField(default=True)

    # Last payment
    last_payment_date = models.DateTimeField(null=True, blank=True)
    last_payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Payment gateway IDs (for recurring payments)
    razorpay_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.tenant.business_name} - {self.plan.name} ({self.status})"

    def save(self, *args, **kwargs):
        """Set trial period on creation"""
        if not self.trial_ends_at:
            self.trial_ends_at = timezone.now() + timedelta(days=14)
        if not self.current_period_start:
            self.current_period_start = timezone.now()
        if not self.current_period_end:
            self.current_period_end = self.trial_ends_at
        super().save(*args, **kwargs)

    def is_active(self):
        """Check if subscription is currently active"""
        now = timezone.now()

        if self.status == 'trial':
            return now <= self.trial_ends_at

        if self.status == 'active':
            return now <= self.current_period_end

        return False

    def days_remaining(self):
        """Days until subscription expires"""
        now = timezone.now()

        if self.status == 'trial':
            delta = self.trial_ends_at - now
        else:
            delta = self.current_period_end - now

        return max(0, delta.days)

    def is_in_grace_period(self):
        """Check if in 7-day grace period after expiry"""
        if self.status in ['past_due', 'expired']:
            grace_end = self.current_period_end + timedelta(days=7)
            return timezone.now() <= grace_end
        return False

    def cancel(self, reason=""):
        """Cancel subscription (immediate)"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.auto_renew = False
        self.save()

    def schedule_cancellation(self):
        """Cancel at end of current period"""
        self.auto_renew = False
        self.save()

    def renew(self, payment_amount=None):
        """Renew subscription for next period"""
        # Determine billing cycle from plan
        if self.plan.price_yearly > 0 and payment_amount and payment_amount >= self.plan.price_yearly:
            # Yearly renewal
            days = 365
        else:
            # Monthly renewal
            days = 30

        self.current_period_start = self.current_period_end
        self.current_period_end = self.current_period_start + timedelta(days=days)
        self.status = 'active'
        self.last_payment_date = timezone.now()

        if payment_amount:
            self.last_payment_amount = payment_amount

        self.save()


class UsageTracking(models.Model):
    """
    Track monthly resource usage for plan limit enforcement
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )

    # Period
    period_month = models.IntegerField()  # 1-12
    period_year = models.IntegerField()   # 2025, 2026, etc.
    period_start = models.DateField()
    period_end = models.DateField()

    # Usage counters
    active_users_count = models.IntegerField(default=0)
    active_locations_count = models.IntegerField(default=0)
    products_count = models.IntegerField(default=0)
    transactions_count = models.IntegerField(default=0)

    # Storage (MB)
    storage_used_mb = models.FloatField(default=0)

    # API calls (if plan includes API)
    api_calls_count = models.IntegerField(default=0)

    # Email/SMS usage
    emails_sent = models.IntegerField(default=0)
    sms_sent = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_year', '-period_month']
        unique_together = [['tenant', 'period_year', 'period_month']]
        verbose_name = "Usage Tracking"
        verbose_name_plural = "Usage Records"
        indexes = [
            models.Index(fields=['tenant', 'period_year', 'period_month']),
        ]

    def __str__(self):
        return f"{self.tenant.business_name} - {self.period_year}/{self.period_month:02d}"

    def is_within_limits(self):
        """Check if current usage is within plan limits"""
        plan = self.tenant.subscription_plan
        violations = []

        if self.active_users_count > plan.max_users:
            violations.append({
                'type': 'users',
                'current': self.active_users_count,
                'limit': plan.max_users,
                'message': f'User limit exceeded: {self.active_users_count}/{plan.max_users}'
            })

        if self.products_count > plan.max_products:
            violations.append({
                'type': 'products',
                'current': self.products_count,
                'limit': plan.max_products,
                'message': f'Product limit exceeded: {self.products_count}/{plan.max_products}'
            })

        if self.transactions_count > plan.max_transactions_per_month:
            violations.append({
                'type': 'transactions',
                'current': self.transactions_count,
                'limit': plan.max_transactions_per_month,
                'message': f'Transaction limit exceeded: {self.transactions_count}/{plan.max_transactions_per_month}'
            })

        return len(violations) == 0, violations

    def get_usage_percentages(self):
        """Get usage as percentage of limits"""
        plan = self.tenant.subscription_plan

        def calc_percentage(current, limit):
            if limit == 0 or limit == 999999:  # Unlimited
                return 0
            return min(100, (current / limit) * 100)

        return {
            'users': {
                'current': self.active_users_count,
                'limit': plan.max_users,
                'percentage': calc_percentage(self.active_users_count, plan.max_users),
            },
            'products': {
                'current': self.products_count,
                'limit': plan.max_products,
                'percentage': calc_percentage(self.products_count, plan.max_products),
            },
            'transactions': {
                'current': self.transactions_count,
                'limit': plan.max_transactions_per_month,
                'percentage': calc_percentage(self.transactions_count, plan.max_transactions_per_month),
            },
        }

    def is_approaching_limit(self, threshold=90):
        """Check if any resource is above threshold% (default 90%)"""
        percentages = self.get_usage_percentages()
        warnings = []

        for resource, data in percentages.items():
            if data['percentage'] >= threshold:
                warnings.append({
                    'resource': resource,
                    'percentage': data['percentage'],
                    'current': data['current'],
                    'limit': data['limit'],
                })

        return len(warnings) > 0, warnings


class PaymentHistory(models.Model):
    """
    Complete payment transaction history
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('manual', 'Manual Entry'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relations
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='payment_history'
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    # Gateway transaction IDs
    razorpay_payment_id = models.CharField(max_length=255, blank=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)

    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)

    # Invoice
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField(default=date.today)

    # Transaction
    transaction_date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)

    # Failure handling
    failure_code = models.CharField(max_length=50, blank=True)
    failure_reason = models.TextField(blank=True)

    # Refund
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    refund_reason = models.TextField(blank=True)

    # Additional data
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "Payment"
        verbose_name_plural = "Payment History"
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['razorpay_payment_id']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.tenant.business_name} - ₹{self.amount} ({self.status})"

    def save(self, *args, **kwargs):
        """Auto-generate invoice number"""
        if not self.invoice_number:
            # Format: INV-2025-11-00001
            year = timezone.now().year
            month = timezone.now().month

            # Count invoices this month
            count = PaymentHistory.objects.filter(
                created_at__year=year,
                created_at__month=month
            ).count() + 1

            self.invoice_number = f'INV-{year}-{month:02d}-{count:05d}'

        super().save(*args, **kwargs)

    def mark_completed(self, payment_id=None):
        """Mark payment as completed"""
        self.status = 'completed'
        self.transaction_date = timezone.now()

        if payment_id:
            if self.payment_method == 'razorpay':
                self.razorpay_payment_id = payment_id
            elif self.payment_method == 'stripe':
                self.stripe_payment_intent_id = payment_id

        self.save()

        # Update subscription
        if self.subscription:
            self.subscription.renew(payment_amount=self.amount)

    def mark_failed(self, reason="", code=""):
        """Mark payment as failed"""
        self.status = 'failed'
        self.failure_reason = reason
        self.failure_code = code
        self.save()

    def process_refund(self, amount=None, reason=""):
        """Process refund"""
        refund_amt = amount or self.amount

        self.status = 'refunded'
        self.refunded_at = timezone.now()
        self.refund_amount = refund_amt
        self.refund_reason = reason
        self.save()