"""
Application configuration for the coupons app.

This file defines metadata for the app and ensures Django registers
the application. See https://docs.djangoproject.com/en/stable/ref/applications/
for more details.
"""

from django.apps import AppConfig


class CouponsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coupons'
    verbose_name = 'Coupons'