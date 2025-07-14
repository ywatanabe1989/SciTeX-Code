# Django Self-Hosting Guide for SciTeX Documentation

## Overview

This guide explains how to integrate SciTeX documentation with your Django platform at `https://scitex.ai`, creating a subdomain `https://docs.scitex.ai` for documentation hosting.

## Architecture Options

### Option 1: Static Files Integration
Serve pre-built Sphinx documentation as static files through Django.

```python
# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'docs/_build/html',  # Sphinx build output
]

# urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Your existing URLs
] + static('docs/', document_root=settings.BASE_DIR / 'docs/_build/html')
```

### Option 2: Subdomain Approach (Recommended)
Configure `docs.scitex.ai` as a separate subdomain serving documentation.

```nginx
# nginx configuration
server {
    server_name docs.scitex.ai;
    
    location / {
        alias /path/to/scitex/docs/_build/html/;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    # Enable gzip for better performance
    gzip on;
    gzip_types text/html text/css application/javascript;
}
```

### Option 3: Django View Integration
Create Django views that serve documentation content.

```python
# views.py
from django.shortcuts import render
from django.http import Http404
from pathlib import Path
import os

def docs_view(request, path=''):
    """Serve documentation pages through Django."""
    docs_root = Path(__file__).parent.parent / 'docs/_build/html'
    
    if not path:
        path = 'index.html'
    elif not path.endswith('.html'):
        path += '.html'
    
    file_path = docs_root / path
    
    if not file_path.exists():
        raise Http404("Documentation page not found")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return HttpResponse(content, content_type='text/html')

# urls.py
urlpatterns = [
    path('docs/', docs_view, name='docs_home'),
    path('docs/<path:path>/', docs_view, name='docs_page'),
]
```

## Automated Documentation Updates

### GitHub Actions Integration

```yaml
# .github/workflows/deploy-docs.yml
name: Deploy Documentation to Django

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  deploy-docs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -e ".[docs]"
    
    - name: Build documentation
      run: |
        cd docs
        make html
    
    - name: Deploy to Django server
      run: |
        # Rsync or SCP to your Django server
        rsync -avz --delete docs/_build/html/ \
          user@scitex.ai:/path/to/django/static/docs/
    
    - name: Restart Django (if needed)
      run: |
        ssh user@scitex.ai "sudo systemctl reload nginx"
```

### Django Management Command

```python
# management/commands/update_docs.py
from django.core.management.base import BaseCommand
import subprocess
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Update SciTeX documentation'
    
    def handle(self, *args, **options):
        docs_dir = Path(__file__).parent.parent.parent.parent / 'docs'
        
        # Pull latest changes
        subprocess.run(['git', 'pull'], cwd=docs_dir.parent)
        
        # Build documentation
        subprocess.run(['make', 'html'], cwd=docs_dir)
        
        # Copy to static files
        subprocess.run([
            'cp', '-r', 
            str(docs_dir / '_build/html/*'),
            '/path/to/django/static/docs/'
        ])
        
        self.stdout.write(
            self.style.SUCCESS('Documentation updated successfully')
        )
```

## Domain Configuration

### DNS Setup
Configure your DNS to point `docs.scitex.ai` to your server:

```
docs.scitex.ai.  300  IN  CNAME  scitex.ai.
```

### SSL Certificate
Use Let's Encrypt for HTTPS:

```bash
sudo certbot --nginx -d docs.scitex.ai
```

## Performance Optimization

### Static File Optimization

```python
# settings.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Enable compression
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    # ... other middleware
]
```

### Caching Strategy

```python
# views.py
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

@cache_page(60 * 60 * 24)  # Cache for 24 hours
@vary_on_headers('Accept-Encoding')
def docs_view(request, path=''):
    # Your documentation serving logic
    pass
```

## Search Integration

### Add Search to Django

```python
# Add to your Django models
from django.db import models

class DocumentationPage(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    url_path = models.CharField(max_length=500)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

# Index documentation content
def index_docs():
    docs_dir = Path('docs/_build/html')
    for html_file in docs_dir.rglob('*.html'):
        # Parse HTML and extract content
        # Save to DocumentationPage model
        pass
```

## Monitoring & Analytics

### Integration with Django Admin

```python
# admin.py
from django.contrib import admin
from .models import DocumentationPage

@admin.register(DocumentationPage)
class DocumentationPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'url_path', 'last_updated']
    search_fields = ['title', 'content']
    list_filter = ['last_updated']
```

### Usage Analytics

```python
# Track documentation usage
from django.db import models

class DocumentationView(models.Model):
    page_path = models.CharField(max_length=500)
    user_ip = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Documentation View"
        verbose_name_plural = "Documentation Views"
```

## Benefits of Django Integration

1. **Unified Authentication**: Use your existing Django user system
2. **Custom Styling**: Match your scitex.ai branding
3. **Advanced Analytics**: Track usage with Django models
4. **Search Integration**: Implement advanced search features
5. **Dynamic Content**: Mix static docs with dynamic Django content
6. **Admin Interface**: Manage documentation through Django admin
7. **API Integration**: Expose documentation through Django REST API

## Implementation Steps

1. Choose architecture option (recommend subdomain)
2. Configure DNS and SSL
3. Set up automated builds with GitHub Actions
4. Implement caching and optimization
5. Add monitoring and analytics
6. Test with staging environment
7. Deploy to production

## Comparison: RTD vs Django Hosting

| Feature | Read the Docs | Django Self-Hosting |
|---------|---------------|-------------------|
| Setup Time | Minutes | Hours |
| Maintenance | Zero | Ongoing |
| Custom Domain | Limited | Full Control |
| Branding | Limited | Complete |
| Analytics | Basic | Advanced |
| Integration | Limited | Full Django |
| Cost | Free/Paid | Server costs |
| Performance | Optimized | Requires optimization |

Both options provide professional documentation hosting - RTD for quick setup, Django for maximum control and integration with your platform.