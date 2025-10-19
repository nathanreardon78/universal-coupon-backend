"""
URL configuration for coupons app.

Defines the route for the coupon creation API endpoint. Prefix these
routes with `/api/` in the project-level URLs to provide a namespaced
API for your web application.
"""

from django.urls import path

from .views import CouponCreateView


urlpatterns = [
    path('coupons/', CouponCreateView.as_view(), name='coupon-create'),
]