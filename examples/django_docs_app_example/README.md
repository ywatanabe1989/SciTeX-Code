# Django Documentation App Example

This directory contains example Django code for serving SciTeX documentation on scitex.ai.

## Structure

```
django_docs_app_example/
├── __init__.py              # Package init
├── views.py                 # Documentation views
├── urls.py                  # URL routing
├── management/
│   ├── __init__.py
│   └── commands/
│       └── update_docs.py   # Management command for updating docs
└── README.md               # This file
```

## Installation

1. Copy this entire directory to your Django project as `docs_app/`

2. Add to your Django settings:
```python
INSTALLED_APPS = [
    # ... existing apps ...
    'docs_app',
]

# Documentation settings
DOCS_ROOT = '/home/ywatanabe/proj/SciTeX-Code/docs/RTD/_build/html'
```

3. Update your main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    path('docs/', include('docs_app.urls')),
]
```

## Usage

### Serving Documentation
Once configured, documentation will be available at:
- `https://scitex.ai/docs/` - Documentation index
- `https://scitex.ai/docs/quickstart` - Quickstart guide
- `https://scitex.ai/docs/modules/` - Module documentation

### Updating Documentation
Run the management command to pull latest changes and rebuild:
```bash
python manage.py update_docs
```

### Automated Updates
Add to crontab for daily updates:
```bash
0 2 * * * cd /path/to/django/project && /path/to/venv/bin/python manage.py update_docs
```

## Features

- **Security**: Path traversal protection
- **Smart Routing**: Automatic .html extension handling
- **Content Types**: Proper MIME type detection
- **Management Command**: Easy documentation updates
- **Error Handling**: User-friendly 404 pages

## Next Steps

1. Configure Nginx for better performance (see django_static_hosting_implementation_20250704.md)
2. Add GitHub webhook for automatic updates
3. Implement search functionality
4. Add version support for multiple documentation versions