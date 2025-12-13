from django.contrib import admin

from .models import Customer, LoyaltyPointsConfig, LoyaltyPointsTransaction

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'loyalty_points_achieved')
    search_fields = ('name', 'email', 'phone_number')
