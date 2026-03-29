"""
Development settings for VoiceTasks.

Extends base settings with dev-specific overrides:
- DEBUG is True
- SQLite database
- Relaxed security settings
"""
from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['*']

# In development, use the insecure but convenient debug toolbar approach
INTERNAL_IPS = ['127.0.0.1']

# Shorter cache timeouts in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Email to console in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
