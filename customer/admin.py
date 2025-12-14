from django.contrib import admin

from .models import Customer, LoyaltyPointsConfig, LoyaltyPointsTransaction

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'loyalty_points_achieved')
    search_fields = ('name', 'email', 'phone_number')

@admin.register(LoyaltyPointsConfig)
class LoyaltyPointsConfigAdmin(admin.ModelAdmin):
    list_display = ('points_per_rupee', 'point_value_in_rupees', 'maximum_redeem_percentage', 'minimum_purchase_amount', 'minimum_points_to_redeem', 'points_expiration_days', 'is_active')
    list_filter = ('points_per_rupee', 'point_value_in_rupees', 'maximum_redeem_percentage', 'minimum_purchase_amount', 'minimum_points_to_redeem', 'points_expiration_days', 'is_active')

@admin.register(LoyaltyPointsTransaction)
class LoyaltyPointsTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_type', 'points', 'points_balance_after', 'sale', 'purchase_amount')
    search_fields = ('sale')
    list_filter = ('customer', 'transaction_type', 'status')