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
from decouple import config
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
import logging
from .models import Coupon


logger = logging.getLogger(__name__)


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for creating or retrieving a coupon."""

    class Meta:
        model = Coupon
        fields = ["email", "website"]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Basic validation to ensure both email and website are present."""
        email = attrs.get("email")
        website = attrs.get("website")
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
        email = validated_data["email"]
        website = validated_data["website"]
        # Check for existing, unredeemed coupon that hasn't expired
        now = timezone.now()
        existing = (
            Coupon.objects.filter(email=email, website=website, redeemed=False)
            .filter(expires_at__gt=now)
            .first()
        )
        if existing:
            return existing
        # Generate a new coupon code; token_hex returns bytes converted to hex
        code = secrets.token_hex(4).upper()  # 8-character code
        expiry_days = int(getattr(settings, "COUPON_EXPIRY_DAYS", 30))
        expires_at = now + timedelta(days=expiry_days)
        coupon = Coupon.objects.create(
            email=email,
            website=website,
            code=code,
            expires_at=expires_at,
            redeemed=False,
        )
        # Send email with coupon code using AWS SES via boto3
        subject = f"Your {int(settings.DISCOUNT_PERCENTAGE) if hasattr(settings, 'DISCOUNT_PERCENTAGE') else 10}% Off Coupon for {website}"
        message = (
            f"Thank you for signing up for exclusive promotions and discounts!\n\n"
            f"Here is your coupon code for {website}: {code}\n"
            f"This code gives you 10% off your next purchase and expires on {expires_at.date()}."
        )
        html_message = f"""
            <html>
            <body>
                <h2>Your Coupon for {website}</h2>
                <p>Thank you for signing up for exclusive promotions and discounts!</p>
                <p><strong>Coupon Code:</strong> <span style='font-size:1.2em;color:#2d7ef7'>{code}</span></p>
                <p>This code gives you <strong>10% off</strong> your next purchase and expires on <strong>{expires_at.date()}</strong>.</p>
                <hr>
                <p style='font-size:0.9em;color:#888'>If you did not request this coupon, please ignore this email.</p>
            </body>
            </html>
        """
        sender = config(
            "SES_SENDER", default=getattr(settings, "DEFAULT_FROM_EMAIL", None)
        )
        aws_access_key = config("AWS_ACCESS_KEY_ID", default=None)
        aws_secret_key = config("AWS_SECRET_ACCESS_KEY", default=None)
        aws_region = config("AWS_REGION_NAME", default="us-east-1")
        if not (aws_access_key and aws_secret_key and sender):
            logger.error("Missing AWS SES credentials or sender email in environment.")
        else:
            ses_client = boto3.client(
                "ses",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region,
            )
            try:
                ses_client.send_email(
                    Source=sender,
                    Destination={"ToAddresses": [email]},
                    Message={
                        "Subject": {"Data": subject},
                        "Body": {
                            "Text": {"Data": message},
                            "Html": {"Data": html_message},
                        },
                    },
                )
            except ClientError as e:
                logger.error(
                    f"Error sending coupon email via SES: {e.response['Error']['Message']}"
                )
            except Exception as e:
                logger.error(f"Unexpected error sending coupon email via SES: {e}")
        return coupon
