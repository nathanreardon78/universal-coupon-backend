"""
Models for the coupons app.

Defines the Coupon model, which stores promotional coupon codes
assigned to user email addresses for specific websites. Coupons can
expire and may be marked as redeemed to prevent reuse. The model
includes minimal fields required for generating and tracking coupons.
"""

from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    """Represents a discount coupon issued to a user for a particular website."""

    email = models.EmailField(help_text="Recipient's email address")
    website = models.CharField(max_length=255, help_text="Site that issued the coupon")
    code = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique coupon code provided to the user",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of creation")
    expires_at = models.DateTimeField(help_text="When the coupon expires")
    redeemed = models.BooleanField(default=False, help_text="Whether the coupon has been used")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'website']),
        ]

    def __str__(self) -> str:
        return f"{self.email} - {self.code}"

    @property
    def is_expired(self) -> bool:
        """Check if the coupon is past its expiry date."""
        return timezone.now() > self.expires_at