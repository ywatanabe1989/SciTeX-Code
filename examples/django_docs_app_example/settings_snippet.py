"""
Django settings snippet for documentation hosting.

Add these settings to your Django project's settings.py or settings/base.py
"""

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ... other apps ...
    'docs_app',  # Add this line
]

# Documentation configuration
DOCS_ROOT = '/home/ywatanabe/proj/SciTeX-Code/docs/RTD/_build/html'

# Optional: Add documentation to static files for development
STATICFILES_DIRS = [
    # ... existing dirs ...
    ('docs', DOCS_ROOT),  # Serve docs as static files in development
]

# Optional: GitHub webhook secret for automated updates
GITHUB_WEBHOOK_SECRET = 'your-webhook-secret-here'  # Generate a secure secret