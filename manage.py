#!/usr/bin/env python
"""
Manage script for Django project.

This script allows you to run administrative tasks for the Django
project. It sets the default settings module and delegates command
execution to Django's command-line utility.

Usage examples:
    python manage.py runserver
    python manage.py migrate

For more information on this file, see the Django documentation:
https://docs.djangoproject.com/en/stable/ref/django-admin/
"""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coupon_project.settings')
    try:
        from django.core.management import execute_from_command_line  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()