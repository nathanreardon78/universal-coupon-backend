"""
Views for coupons app.

Defines a simple API endpoint for generating coupons. The endpoint
accepts POST requests with an email address and website name, returning
either an existing valid coupon or creating a new one. The response
includes the coupon code and expiry information.
"""

from rest_framework import generics, status
from rest_framework.response import Response

from .models import Coupon
from .serializers import CouponSerializer


class CouponCreateView(generics.CreateAPIView):
    """API view for creating or retrieving a coupon."""

    serializer_class = CouponSerializer

    def create(self, request, *args, **kwargs):  # type: ignore[override]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        coupon = serializer.save()
        data = {
            'email': coupon.email,
            'website': coupon.website,
            'code': coupon.code,
            'expires_at': coupon.expires_at,
        }
        return Response(data, status=status.HTTP_201_CREATED)