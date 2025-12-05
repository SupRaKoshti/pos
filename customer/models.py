from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.models import BaseModel


class Customer(BaseModel):
    """
    Customer model to store customer information
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    loyalty_points_achieved = models.IntegerField(default=0)
    loyalty_points_redeemed = models.IntegerField(default=0)

    @property
    def loyalty_points_balance(self):
        """Calculate current available loyalty points balance"""
        return self.loyalty_points_achieved - self.loyalty_points_redeemed
    
    @property
    def loyalty_points_value(self):
        """Calculate rupee value of available loyalty points"""
        try:
            config = LoyaltyPointsConfig.objects.get(tenant=self.tenant, is_active=True)
            return config.calculate_rupees_from_points(self.loyalty_points_balance)
        except LoyaltyPointsConfig.DoesNotExist:
            return Decimal('0.00')
    
    def get_expiring_points(self, days_ahead=30):
        """Get points that will expire within specified days"""
        expiry_date = timezone.now() + timedelta(days=days_ahead)
        
        expiring_transactions = self.loyalty_transactions.filter(
            transaction_type='earned',
            is_expired=False,
            expires_at__lte=expiry_date,
            expires_at__gt=timezone.now()
        )
        
        total_expiring = sum(abs(t.points) for t in expiring_transactions)
        return total_expiring
    
    def can_redeem_points(self, bill_amount):
        """Check if customer can redeem points for given bill amount"""
        try:
            config = LoyaltyPointsConfig.objects.get(tenant=self.tenant, is_active=True)
            
            if not config.is_active:
                return False, "Loyalty points program is not active"
            
            if bill_amount < config.minimum_purchase_amount:
                return False, f"Minimum purchase amount of ₹{config.minimum_purchase_amount} required"
            
            if self.loyalty_points_balance < config.minimum_points_to_redeem:
                return False, f"Minimum {config.minimum_points_to_redeem} points required to redeem"
            
            max_redeemable = config.calculate_max_points_redeemable(
                bill_amount, 
                self.loyalty_points_balance
            )
            
            if max_redeemable < config.minimum_points_to_redeem:
                return False, "Not enough points to redeem for this bill amount"
            
            return True, f"Can redeem up to {max_redeemable} points"
        except LoyaltyPointsConfig.DoesNotExist:
            return False, "Loyalty points configuration not found"

    def __str__(self):
        return self.name


class LoyaltyPointsConfig(BaseModel):
    """
    Configuration model for Loyalty Points Program
    Stores global settings for the loyalty points system per tenant
    """
    
    # Point Earning Configuration
    points_per_rupee = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Number of points earned per rupee spent (e.g., 1.0 = 1 point per ₹1)'
    )
    
    # Point Redemption Configuration
    point_value_in_rupees = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.10'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Value of 1 point in rupees (e.g., 0.10 = 1 point = ₹0.10)'
    )
    
    maximum_redeem_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('50.00'),
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))],
        help_text='Maximum percentage of bill amount that can be redeemed using points (0-100)'
    )
    
    minimum_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum purchase amount required to earn/redeem points'
    )
    
    minimum_points_to_redeem = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text='Minimum points required to redeem'
    )
    
    # Expiration Configuration
    points_expiration_days = models.IntegerField(
        default=365,
        validators=[MinValueValidator(1)],
        help_text='Number of days after which points expire (0 = no expiration)'
    )
    
    # Program Status
    is_active = models.BooleanField(
        default=True,
        help_text='Enable/disable loyalty points program'
    )
    
    # Additional Settings
    allow_partial_redemption = models.BooleanField(
        default=True,
        help_text='Allow customers to redeem partial points'
    )
    
    round_points = models.BooleanField(
        default=True,
        help_text='Round points to nearest integer when calculating'
    )
    
    class Meta:
        verbose_name = "Loyalty Points Configuration"
        verbose_name_plural = "Loyalty Points Configurations"
        unique_together = ['tenant']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Loyalty Config - {self.tenant.business_name if hasattr(self, 'tenant') else 'N/A'}"
    
    def calculate_points_earned(self, purchase_amount):
        """
        Calculate points earned based on purchase amount
        """
        if purchase_amount < self.minimum_purchase_amount:
            return 0
        
        points = float(purchase_amount) * float(self.points_per_rupee)
        
        if self.round_points:
            return int(round(points))
        return int(points)
    
    def calculate_rupees_from_points(self, points):
        """
        Calculate rupee value from points
        """
        return Decimal(points) * self.point_value_in_rupees
    
    def calculate_max_redeemable_amount(self, bill_amount):
        """
        Calculate maximum amount that can be redeemed from bill using points
        """
        max_redeem_amount = (bill_amount * self.maximum_redeem_percentage) / Decimal('100.00')
        return max_redeem_amount
    
    def calculate_max_points_redeemable(self, bill_amount, available_points):
        """
        Calculate maximum points that can be redeemed for a given bill amount
        """
        max_redeem_amount = self.calculate_max_redeemable_amount(bill_amount)
        max_points_by_amount = max_redeem_amount / self.point_value_in_rupees
        
        # Can't redeem more than available points
        max_points = min(int(max_points_by_amount), available_points)
        
        # Must meet minimum points requirement
        if max_points < self.minimum_points_to_redeem:
            return 0
        
        return max_points


class LoyaltyPointsTransaction(BaseModel):
    """
    Transaction model to track all loyalty points earned and redeemed
    Provides complete audit trail for loyalty points
    """
    
    TRANSACTION_TYPES = [
        ('earned', 'Points Earned'),
        ('redeemed', 'Points Redeemed'),
        ('expired', 'Points Expired'),
        ('adjusted', 'Points Adjusted'),
        ('refunded', 'Points Refunded'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='loyalty_transactions',
        help_text='Customer associated with this transaction'
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        help_text='Type of loyalty points transaction'
    )
    
    points = models.IntegerField(
        help_text='Number of points (positive for earned, negative for redeemed)'
    )
    
    points_balance_after = models.IntegerField(
        default=0,
        help_text='Customer points balance after this transaction'
    )
    
    # Related Sale (if applicable)
    sale = models.ForeignKey(
        'sales.Sale',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_transactions',
        help_text='Sale transaction associated with this points transaction'
    )
    
    # Financial Details
    purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Purchase amount that generated this transaction'
    )
    
    redemption_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Amount redeemed using points'
    )
    
    # Expiration Tracking
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date when these points expire (for earned points)'
    )
    
    is_expired = models.BooleanField(
        default=False,
        help_text='Whether these points have expired'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed',
        help_text='Transaction status'
    )
    
    # Reference and Notes
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='External reference number (e.g., invoice number)'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Additional notes or description'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata in JSON format'
    )
    
    class Meta:
        verbose_name = "Loyalty Points Transaction"
        verbose_name_plural = "Loyalty Points Transactions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'transaction_type']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['expires_at', 'is_expired']),
            models.Index(fields=['sale']),
        ]
    
    def __str__(self):
        return f"{self.customer.name} - {self.get_transaction_type_display()} - {abs(self.points)} points"
    
    def save(self, *args, **kwargs):
        """
        Auto-calculate expiration date and update customer points
        """
        # Set expiration date for earned points
        if self.transaction_type == 'earned' and not self.expires_at:
            config = LoyaltyPointsConfig.objects.filter(tenant=self.tenant).first()
            if config and config.points_expiration_days > 0:
                self.expires_at = timezone.now() + timedelta(days=config.points_expiration_days)
        
        # Update customer points balance
        if self.status == 'completed' and not self.pk:
            if self.transaction_type == 'earned':
                self.customer.loyalty_points_achieved += self.points
            elif self.transaction_type in ['redeemed', 'expired', 'refunded']:
                self.customer.loyalty_points_redeemed += abs(self.points)
            
            self.customer.save()
            self.points_balance_after = self.customer.loyalty_points_balance
        
        super().save(*args, **kwargs)
    
    def mark_expired(self):
        """
        Mark this transaction as expired
        """
        if self.transaction_type == 'earned' and not self.is_expired:
            expired_points = abs(self.points)
            self.is_expired = True
            self.status = 'completed'
            self.save()
            
            # Create expiration transaction (save method will update customer points)
            expiration_txn = LoyaltyPointsTransaction(
                tenant=self.tenant,
                customer=self.customer,
                transaction_type='expired',
                points=-expired_points,
                notes=f'Points expired from transaction {self.id}',
                status='completed'
            )
            expiration_txn.save()
    
    def cancel(self, reason=""):
        """
        Cancel this transaction and reverse points
        """
        if self.status == 'completed':
            # Reverse the points
            if self.transaction_type == 'earned':
                self.customer.loyalty_points_achieved -= self.points
            elif self.transaction_type in ['redeemed', 'expired', 'refunded']:
                self.customer.loyalty_points_redeemed -= abs(self.points)
            
            self.customer.save()
            self.status = 'cancelled'
            self.notes += f"\nCancelled: {reason}"
            self.save()