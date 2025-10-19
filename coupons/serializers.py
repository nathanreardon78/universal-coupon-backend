"""
Serializers for coupons app.

Defines a serializer for generating coupons via a REST API. The serializer
handles creating a new coupon if one does not already exist for a given
email and website combination, or returns an existing, non-expired coupon.
It also triggers sending the coupon code via email.
"""

import secrets
from datetime import timedelta
from typing import Any, Dict

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers

from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for creating or retrieving a coupon."""

    class Meta:
        model = Coupon
        fields = ['email', 'website']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Basic validation to ensure both email and website are present."""
        email = attrs.get('email')
        website = attrs.get('website')
        if not email or not website:
            raise serializers.ValidationError("Email and website are required.")
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Coupon:
        """
        Either return an existing valid coupon or create a new one.

        A coupon is considered valid if it has not expired and has not been
        redeemed. When a new coupon is created, an email is dispatched to
        the user containing the coupon code.
        """
        email = validated_data['email']
        website = validated_data['website']
        # Check for existing, unredeemed coupon that hasn't expired
        now = timezone.now()
        existing = (
            Coupon.objects
            .filter(email=email, website=website, redeemed=False)
            .filter(expires_at__gt=now)
            .first()
        )
        if existing:
            return existing
        # Generate a new coupon code; token_hex returns bytes converted to hex
        code = secrets.token_hex(4).upper()  # 8-character code
        expiry_days = int(getattr(settings, 'COUPON_EXPIRY_DAYS', 30))
        expires_at = now + timedelta(days=expiry_days)
        coupon = Coupon.objects.create(
            email=email,
            website=website,
            code=code,
            expires_at=expires_at,
            redeemed=False,
        )
        # Send email with coupon code
        subject = f"Your {int(settings.DISCOUNT_PERCENTAGE) if hasattr(settings, 'DISCOUNT_PERCENTAGE') else 10}% Off Coupon for {website}"
        message = (
            f"Thank you for signing up for exclusive promotions and discounts!\n\n"
            f"Here is your coupon code for {website}: {code}\n"
            f"This code gives you 10% off your next purchase and expires on {expires_at.date()}."
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
        except Exception:
            # In production you might log this error. For now we silently
            # ignore exceptions to avoid breaking the API response.
            pass
        return coupon