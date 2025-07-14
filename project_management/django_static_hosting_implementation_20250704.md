<!-- ---
!-- Timestamp: 2025-07-04 20:50:00
!-- Author: Claude
!-- File: /home/ywatanabe/proj/SciTeX-Code/project_management/django_static_hosting_implementation_20250704.md
!-- --- -->

# Django Static Hosting Implementation - Step by Step

## Overview
This guide provides a complete implementation for hosting SciTeX documentation on scitex.ai using Django's static file serving (Option 1 from the hosting guide).

## Prerequisites
- Django project for scitex.ai
- Nginx web server
- Built SciTeX documentation in `docs/RTD/_build/html/`

## Step 1: Build Documentation

First, ensure the documentation is built and up-to-date:

```bash
cd /home/ywatanabe/proj/SciTeX-Code/docs/RTD
make clean
make html
```

Verify the build succeeded:
```bash
ls -la _build/html/
# Should see index.html and other documentation files
```

## Step 2: Create Documentation App in Django

Create a dedicated app for serving documentation:

```bash
cd /path/to/scitex.ai/django/project
python manage.py startapp docs_app
```

## Step 3: Configure Django Settings

Add to your Django settings file:

```python
# settings.py or settings/base.py

INSTALLED_APPS = [
    # ... existing apps ...
    'docs_app',
]

# Static files configuration
STATICFILES_DIRS = [
    # ... existing dirs ...
    ('docs', '/home/ywatanabe/proj/SciTeX-Code/docs/RTD/_build/html'),
]

# Documentation settings
DOCS_ROOT = '/home/ywatanabe/proj/SciTeX-Code/docs/RTD/_build/html'
```

## Step 4: Create Documentation Views

Create `docs_app/views.py`:

```python
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse, Http404
from django.conf import settings
import os
import mimetypes

class DocumentationView(TemplateView):
    """Serve static documentation with proper content types."""
    
    def get(self, request, path=''):
        # Default to index.html if no path specified
        if not path:
            path = 'index.html'
        
        # Construct full file path
        file_path = os.path.join(settings.DOCS_ROOT, path)
        
        # Security check - prevent directory traversal
        if not os.path.abspath(file_path).startswith(settings.DOCS_ROOT):
            raise Http404("Invalid path")
        
        # Check if file exists
        if not os.path.exists(file_path):
            # Try with .html extension
            html_path = file_path + '.html'
            if os.path.exists(html_path):
                file_path = html_path
            else:
                raise Http404("Documentation page not found")
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'text/html'
        
        # Read and serve file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return HttpResponse(content, content_type=content_type)
        except IOError:
            raise Http404("Error reading documentation file")

class DocumentationRedirectView(TemplateView):
    """Redirect /docs/ to /docs/index.html"""
    
    def get(self, request):
        return redirect('docs:documentation', path='index.html')
```

## Step 5: Configure URLs

Create `docs_app/urls.py`:

```python
from django.urls import path, re_path
from .views import DocumentationView, DocumentationRedirectView

app_name = 'docs'

urlpatterns = [
    path('', DocumentationRedirectView.as_view(), name='documentation_home'),
    re_path(r'^(?P<path>.*)$', DocumentationView.as_view(), name='documentation'),
]
```

Update main project `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... other URL patterns ...
    path('docs/', include('docs_app.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Step 6: Create Management Command for Updates

Create `docs_app/management/commands/update_docs.py`:

```python
from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os
import shutil

class Command(BaseCommand):
    help = 'Update SciTeX documentation from repository'

    def handle(self, *args, **options):
        scitex_path = '/home/ywatanabe/proj/SciTeX-Code'
        docs_path = os.path.join(scitex_path, 'docs/RTD')
        
        self.stdout.write('Updating SciTeX repository...')
        
        # Pull latest changes
        subprocess.run(['git', 'pull'], cwd=scitex_path, check=True)
        
        self.stdout.write('Building documentation...')
        
        # Clean and build docs
        subprocess.run(['make', 'clean'], cwd=docs_path, check=True)
        subprocess.run(['make', 'html'], cwd=docs_path, check=True)
        
        self.stdout.write(self.style.SUCCESS('Documentation updated successfully!'))
```

## Step 7: Configure Nginx

Add to your Nginx configuration:

```nginx
server {
    listen 80;
    server_name scitex.ai www.scitex.ai;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name scitex.ai www.scitex.ai;
    
    # SSL configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    
    # Documentation specific configuration
    location /docs/ {
        alias /home/ywatanabe/proj/SciTeX-Code/docs/RTD/_build/html/;
        try_files $uri $uri/ $uri.html =404;
        
        # Enable compression
        gzip on;
        gzip_types text/html text/css application/javascript;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /path/to/django/static/;
    }
    
    # Media files
    location /media/ {
        alias /path/to/django/media/;
    }
}
```

## Step 8: Add Navigation Link

Update your Django base template:

```html
<!-- templates/base.html or similar -->
<nav class="navbar">
    <div class="nav-links">
        <a href="{% url 'home' %}">Home</a>
        <a href="{% url 'docs:documentation_home' %}">Documentation</a>
        <a href="{% url 'api' %}">API</a>
        <!-- other navigation items -->
    </div>
</nav>
```

## Step 9: Create GitHub Webhook (Optional)

Create `docs_app/views.py` webhook handler:

```python
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.management import call_command

@csrf_exempt
def github_webhook(request):
    """Handle GitHub webhook for automatic documentation updates."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Verify GitHub signature (optional but recommended)
    signature = request.headers.get('X-Hub-Signature-256')
    if signature:
        secret = settings.GITHUB_WEBHOOK_SECRET.encode()
        expected_signature = 'sha256=' + hmac.new(
            secret,
            request.body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return JsonResponse({'error': 'Invalid signature'}, status=401)
    
    # Parse webhook payload
    import json
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Check if push to main branch
    if payload.get('ref') == 'refs/heads/main':
        # Update documentation asynchronously
        from django.core.management import call_command
        from threading import Thread
        
        def update_docs():
            call_command('update_docs')
        
        thread = Thread(target=update_docs)
        thread.start()
        
        return JsonResponse({'status': 'Documentation update started'})
    
    return JsonResponse({'status': 'No action taken'})
```

Add to `docs_app/urls.py`:
```python
urlpatterns = [
    # ... existing patterns ...
    path('webhook/', github_webhook, name='github_webhook'),
]
```

## Step 10: Test the Implementation

1. **Run Django development server:**
   ```bash
   python manage.py runserver
   ```

2. **Test documentation access:**
   - Visit http://localhost:8000/docs/
   - Should redirect to documentation index
   - Navigate through documentation pages

3. **Test static assets:**
   - Check CSS/JS loading
   - Verify images display correctly

4. **Test search functionality:**
   - Documentation search should work

## Step 11: Deploy to Production

1. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

2. **Restart services:**
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

3. **Test production URLs:**
   - https://scitex.ai/docs/
   - https://scitex.ai/docs/api/
   - https://scitex.ai/docs/tutorials/

## Step 12: Set Up Automated Updates

Create a cron job for regular updates:

```bash
# Edit crontab
crontab -e

# Add this line to update docs daily at 2 AM
0 2 * * * cd /path/to/django/project && /path/to/venv/bin/python manage.py update_docs
```

## Troubleshooting

### Common Issues:

1. **404 errors on documentation pages:**
   - Check DOCS_ROOT path in settings
   - Verify documentation is built
   - Check file permissions

2. **CSS/JS not loading:**
   - Run `python manage.py collectstatic`
   - Check STATIC_URL configuration
   - Verify Nginx static file location

3. **Search not working:**
   - Ensure searchindex.js is accessible
   - Check browser console for errors

### Debug Commands:

```bash
# Check if documentation files exist
ls -la /home/ywatanabe/proj/SciTeX-Code/docs/RTD/_build/html/

# Test Django can access files
python manage.py shell
>>> from django.conf import settings
>>> import os
>>> os.path.exists(os.path.join(settings.DOCS_ROOT, 'index.html'))

# Check Nginx configuration
sudo nginx -t
```

## Security Considerations

1. **Path Traversal Protection:**
   - The view includes security checks to prevent accessing files outside DOCS_ROOT

2. **Content Type Headers:**
   - Properly set based on file extension

3. **HTTPS Only:**
   - Nginx configured to redirect HTTP to HTTPS

4. **Webhook Security:**
   - Verify GitHub signatures if using webhooks

## Next Steps

1. **Monitor Performance:**
   - Set up monitoring for documentation access
   - Track page load times

2. **Add Analytics:**
   - Integrate Google Analytics or similar
   - Track documentation usage patterns

3. **Enhance Search:**
   - Consider adding Algolia or similar for better search

4. **Version Support:**
   - Add support for multiple documentation versions

## Completion Checklist

- [ ] Documentation built in docs/RTD/_build/html/
- [ ] Django docs_app created
- [ ] Settings configured with DOCS_ROOT
- [ ] Views and URLs configured
- [ ] Nginx configuration updated
- [ ] Navigation links added
- [ ] Static files collected
- [ ] Production deployment tested
- [ ] Automated updates configured
- [ ] Security measures implemented

Once all items are checked, your SciTeX documentation will be live at https://scitex.ai/docs/!

<!-- EOF -->