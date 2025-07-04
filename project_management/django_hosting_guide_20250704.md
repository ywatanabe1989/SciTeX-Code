<!-- ---
!-- Timestamp: 2025-07-04 20:44:00
!-- Author: Claude
!-- File: /home/ywatanabe/proj/SciTeX-Code/project_management/django_hosting_guide_20250704.md
!-- --- -->

# Django Documentation Hosting Guide - scitex.ai

## Overview
Guide for hosting SciTeX documentation on the Django-powered scitex.ai website.

## Current Documentation Status
- ✅ Sphinx documentation built and ready in `docs/RTD/_build/html/`
- ✅ Read the Docs configuration complete
- ✅ 25+ notebooks converted to documentation
- ✅ API reference and tutorials ready

## Hosting Options for scitex.ai

### Option 1: Static Files Through Django (Recommended)
Serve the built HTML documentation as static files.

#### Implementation Steps:
1. **Build Documentation**
   ```bash
   cd docs/RTD
   make clean
   make html
   ```

2. **Copy to Django Static Directory**
   ```bash
   # In your Django project
   cp -r /path/to/SciTeX-Code/docs/RTD/_build/html/* /path/to/django/static/docs/
   ```

3. **Configure Django URLs**
   ```python
   # In Django urls.py
   from django.urls import path
   from django.views.generic import RedirectView
   from django.conf import settings
   from django.conf.urls.static import static
   
   urlpatterns = [
       # ... existing patterns ...
       path('docs/', RedirectView.as_view(url='/static/docs/index.html')),
   ]
   
   if settings.DEBUG:
       urlpatterns += static('/static/docs/', document_root=settings.STATICFILES_DIRS[0] + '/docs/')
   ```

4. **Configure Nginx (Production)**
   ```nginx
   location /docs/ {
       alias /path/to/static/docs/;
       try_files $uri $uri/ /docs/index.html;
   }
   ```

### Option 2: Subdomain (docs.scitex.ai)
Host documentation on a separate subdomain.

#### Implementation Steps:
1. **DNS Configuration**
   - Add CNAME record: `docs.scitex.ai` → your server

2. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name docs.scitex.ai;
       
       root /path/to/SciTeX-Code/docs/RTD/_build/html;
       index index.html;
       
       location / {
           try_files $uri $uri/ =404;
       }
   }
   ```

3. **SSL Certificate**
   ```bash
   certbot --nginx -d docs.scitex.ai
   ```

### Option 3: Django View Integration
Integrate documentation directly into Django views.

#### Implementation Steps:
1. **Create Documentation App**
   ```bash
   python manage.py startapp docs_app
   ```

2. **Create View**
   ```python
   # docs_app/views.py
   from django.shortcuts import render
   from django.views.generic import TemplateView
   import os
   
   class DocumentationView(TemplateView):
       def get(self, request, path='index.html'):
           doc_root = '/path/to/SciTeX-Code/docs/RTD/_build/html'
           file_path = os.path.join(doc_root, path)
           
           if os.path.exists(file_path):
               with open(file_path, 'r') as f:
                   content = f.read()
               return render(request, 'docs_wrapper.html', {'content': content})
           else:
               return render(request, '404.html', status=404)
   ```

3. **URL Configuration**
   ```python
   # docs_app/urls.py
   from django.urls import path
   from .views import DocumentationView
   
   urlpatterns = [
       path('<path:path>', DocumentationView.as_view(), name='documentation'),
       path('', DocumentationView.as_view(), name='documentation_home'),
   ]
   ```

## Automated Build Integration

### GitHub Actions Webhook
1. **Add to Django**
   ```python
   # webhook/views.py
   @csrf_exempt
   def github_webhook(request):
       if request.method == 'POST':
           # Verify GitHub signature
           # Trigger documentation build
           subprocess.run(['make', '-C', '/path/to/docs/RTD', 'html'])
           # Copy to static directory
           return JsonResponse({'status': 'success'})
   ```

2. **Configure GitHub Webhook**
   - Repository Settings → Webhooks
   - URL: `https://scitex.ai/webhook/docs-build/`
   - Events: Push to main branch

## Search Integration

### Add Sphinx Search to Django
```python
# Add to Django template
<script type="text/javascript" src="{% static 'docs/_static/searchtools.js' %}"></script>
<script type="text/javascript" src="{% static 'docs/searchindex.js' %}"></script>
```

## Navigation Integration

### Link from Main Site
```html
<!-- In Django navigation template -->
<nav>
    <a href="/">Home</a>
    <a href="/docs/">Documentation</a>
    <a href="/api/">API</a>
</nav>
```

## Maintenance Tasks

### Update Documentation
```bash
#!/bin/bash
# update_docs.sh
cd /path/to/SciTeX-Code
git pull
cd docs/RTD
make clean
make html
cp -r _build/html/* /path/to/django/static/docs/
# Restart Django if needed
```

### Cron Job for Regular Updates
```cron
# Update docs daily at 2 AM
0 2 * * * /path/to/update_docs.sh
```

## Security Considerations

1. **Access Control**
   ```python
   # For private documentation
   from django.contrib.auth.decorators import login_required
   
   @login_required
   def secure_docs_view(request):
       # Serve documentation only to authenticated users
   ```

2. **CORS Headers**
   ```python
   # If serving from different domain
   CORS_ALLOWED_ORIGINS = [
       "https://scitex.ai",
       "https://docs.scitex.ai",
   ]
   ```

## Recommended Approach

For scitex.ai, **Option 1 (Static Files)** is recommended because:
- Simple to implement
- Good performance (served directly by web server)
- Easy to update
- Works well with existing Django setup
- Can be automated with GitHub webhooks

## Next Steps

1. Choose hosting approach
2. Build documentation: `cd docs/RTD && make html`
3. Implement chosen option in Django project
4. Test documentation access
5. Set up automated updates
6. Configure search functionality
7. Add analytics tracking

## Testing URLs
After implementation, documentation will be available at:
- Option 1: `https://scitex.ai/docs/`
- Option 2: `https://docs.scitex.ai/`
- Option 3: `https://scitex.ai/documentation/`

<!-- EOF -->