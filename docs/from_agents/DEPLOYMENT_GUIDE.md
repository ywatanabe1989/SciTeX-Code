# SciTeX Documentation Deployment Guide

## Quick Start Decision Matrix

| Use Case | Recommended Option | Setup Time |
|----------|-------------------|------------|
| Quick professional docs | Read the Docs | 5 minutes |
| Full control + Django integration | Self-hosting | 2-4 hours |
| Testing/preview | Local build | 1 minute |

## Option 1: Read the Docs (Recommended for Most Users)

### Prerequisites
- GitHub account: `ywatanabe1989` ✅
- Repository: `SciTeX-Code` ✅ 
- Configuration files: ✅ Ready

### Step-by-Step Deployment

1. **Connect Repository**
   ```
   1. Visit https://readthedocs.org/
   2. Sign in with GitHub (ywatanabe1989)
   3. Go to "My Projects" → "Import a Project"
   4. Select "SciTeX-Code" repository
   5. Click "Next"
   ```

2. **Configure Project**
   ```
   Project Details:
   - Name: scitex
   - Repository URL: https://github.com/ywatanabe1989/SciTeX-Code
   - Default branch: develop (or main)
   - Language: English
   - Programming Language: Python
   ```

3. **Advanced Settings**
   ```
   - Python Interpreter: CPython 3.11
   - Use system packages: No
   - Requirements file: docs/requirements.txt
   - Python configuration file: setup.cfg
   - Documentation type: Sphinx Html
   ```

4. **Build Configuration** (Auto-detected)
   - `.readthedocs.yaml` ✅ Configured
   - `docs/conf.py` ✅ Enhanced  
   - `docs/requirements.txt` ✅ Ready
   - `setup.cfg` ✅ Updated

5. **First Build**
   - Click "Build Version" 
   - Monitor build logs
   - Fix any issues (rare with our setup)

6. **Access Documentation**
   ```
   Primary URL: https://scitex.readthedocs.io/
   Branch URLs: https://scitex.readthedocs.io/en/develop/
   ```

### Custom Domain (Optional)
```
1. RTD Admin → Domains → Add Domain
2. Domain: docs.scitex.ai
3. Canonical: Yes
4. Configure DNS: CNAME docs.scitex.ai → scitex.readthedocs.io
5. Enable HTTPS (automatic)
```

## Option 2: Django Self-Hosting on scitex.ai

### Prerequisites
- Django server at `scitex.ai` ✅
- SSH access to server
- Nginx/Apache web server
- Python 3.11+ environment

### Architecture Decision

**Recommended: Subdomain Approach**
- URL: `https://docs.scitex.ai`
- Separate from main Django app
- Easier maintenance and updates
- Better performance

### Step-by-Step Implementation

1. **Server Preparation**
   ```bash
   # On your scitex.ai server
   sudo mkdir -p /var/www/docs.scitex.ai
   sudo chown -R $USER:$USER /var/www/docs.scitex.ai
   
   # Clone repository
   cd /var/www/docs.scitex.ai
   git clone https://github.com/ywatanabe1989/SciTeX-Code.git
   cd SciTeX-Code
   ```

2. **Build Documentation**
   ```bash
   # Install dependencies
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[docs]"
   
   # Build docs
   cd docs
   make html
   ```

3. **Nginx Configuration**
   ```nginx
   # /etc/nginx/sites-available/docs.scitex.ai
   server {
       listen 80;
       server_name docs.scitex.ai;
       
       root /var/www/docs.scitex.ai/SciTeX-Code/docs/_build/html;
       index index.html;
       
       location / {
           try_files $uri $uri/ =404;
       }
       
       # Optimize static files
       location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
       
       # Enable gzip
       gzip on;
       gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
   }
   ```

4. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/docs.scitex.ai /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

5. **SSL Certificate**
   ```bash
   sudo certbot --nginx -d docs.scitex.ai
   ```

6. **Automated Updates**
   ```bash
   # Create update script
   cat > /var/www/docs.scitex.ai/update_docs.sh << 'EOF'
   #!/bin/bash
   cd /var/www/docs.scitex.ai/SciTeX-Code
   git pull origin develop
   source ../venv/bin/activate
   cd docs
   make html
   EOF
   
   chmod +x /var/www/docs.scitex.ai/update_docs.sh
   
   # Setup cron job
   crontab -e
   # Add: 0 */6 * * * /var/www/docs.scitex.ai/update_docs.sh
   ```

### Django Integration (Optional Enhancement)

If you want deeper integration with your Django app:

```python
# In your main Django project
# urls.py
urlpatterns = [
    # Existing URLs
    path('docs/', include('docs.urls')),
]

# docs/urls.py  
from django.urls import path
from . import views

urlpatterns = [
    path('', views.docs_redirect),
    path('<path:doc_path>/', views.serve_docs),
]

# docs/views.py
from django.shortcuts import redirect
from django.http import FileResponse, Http404
from pathlib import Path

def docs_redirect(request):
    return redirect('https://docs.scitex.ai/')

def serve_docs(request, doc_path):
    # Serve through Django with authentication, analytics, etc.
    pass
```

## Option 3: Local Development/Testing

### Quick Local Build
```bash
cd SciTeX-Code
pip install -e ".[docs]"
cd docs
make html
open _build/html/index.html
```

### Live Reload During Development
```bash
pip install sphinx-autobuild
sphinx-autobuild docs docs/_build/html --host 0.0.0.0 --port 8000
# Visit http://localhost:8000
```

## Comparison Summary

### Read the Docs Pros/Cons
✅ **Pros:**
- Zero maintenance
- Professional hosting
- Multiple formats (HTML, PDF, ePub)
- Built-in search
- Version management
- Free for open source

❌ **Cons:**
- Limited customization
- RTD branding
- Build time limits
- Less control

### Django Self-Hosting Pros/Cons
✅ **Pros:**
- Complete control
- Custom branding/styling
- Integration with existing platform
- Advanced analytics
- Custom authentication
- No external dependencies

❌ **Cons:**
- Server maintenance required
- SSL certificate management
- Build infrastructure needed
- Higher complexity
- Ongoing costs

## Recommended Deployment Strategy

### Phase 1: Quick Launch (RTD)
1. Deploy to Read the Docs immediately
2. URL: `https://scitex.readthedocs.io/`
3. Start gathering user feedback

### Phase 2: Custom Domain (RTD + Custom Domain)
1. Configure `docs.scitex.ai` → RTD
2. Professional URL with RTD benefits
3. Minimal maintenance overhead

### Phase 3: Full Integration (Optional)
1. Migrate to Django self-hosting
2. Deep integration with scitex.ai platform
3. Advanced features and analytics

## Monitoring & Maintenance

### RTD Monitoring
- Build status emails
- Analytics dashboard
- Error notifications

### Self-Hosting Monitoring
```bash
# Health check script
curl -f https://docs.scitex.ai/ || echo "Docs site down"

# Log monitoring
tail -f /var/log/nginx/docs.scitex.ai.access.log
```

### Automated Testing
```yaml
# .github/workflows/test-docs.yml
name: Test Documentation Build

on: [push, pull_request]

jobs:
  test-docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: |
        pip install -e ".[docs]"
        cd docs
        make html
        # Test for broken links
        make linkcheck
```

## Final Recommendation

**Start with Read the Docs** using your `ywatanabe1989` account:

1. **Immediate benefits**: Professional documentation live in minutes
2. **Zero maintenance**: Focus on content, not infrastructure  
3. **Future flexibility**: Can always migrate to self-hosting later
4. **Professional URL**: Configure `docs.scitex.ai` to point to RTD

The RTD setup is ready to deploy with all configuration files in place. Your documentation will include 44+ example notebooks, complete API reference, and professional presentation.

**Next Action**: Visit https://readthedocs.org/ and import your SciTeX-Code repository!