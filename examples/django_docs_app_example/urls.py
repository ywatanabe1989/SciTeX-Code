"""
Django URL configuration for documentation app.

This is an example implementation that can be copied to the Django project.
Path: docs_app/urls.py
"""

from django.urls import path, re_path
from .views import DocumentationView, DocumentationRedirectView

app_name = 'docs'

urlpatterns = [
    path('', DocumentationRedirectView.as_view(), name='documentation_home'),
    re_path(r'^(?P<path>.*)$', DocumentationView.as_view(), name='documentation'),
]