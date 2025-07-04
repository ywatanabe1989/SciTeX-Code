"""
Django views for serving SciTeX documentation.

This is an example implementation that can be copied to the Django project.
Path: docs_app/views.py
"""

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