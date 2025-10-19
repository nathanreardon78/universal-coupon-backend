"""
Admin configuration for coupons app.

Registers the Coupon model with the Django admin site so that coupons
can be viewed and managed through the admin interface.
"""

from django.contrib import admin

from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('email', 'website', 'code', 'created_at', 'expires_at', 'redeemed')
    search_fields = ('email', 'website', 'code')
    list_filter = ('website', 'redeemed', 'expires_at')