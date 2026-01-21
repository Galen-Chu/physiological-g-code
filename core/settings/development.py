"""
Development settings for Physiological G-Code.
"""

from .base import *

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Allow all CORS origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Show emails in console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar
INTERNAL_IPS = ['127.0.0.1', 'localhost']
