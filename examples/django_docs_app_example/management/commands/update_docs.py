"""
Django management command to update SciTeX documentation.

This is an example implementation that can be copied to the Django project.
Path: docs_app/management/commands/update_docs.py

Usage:
    python manage.py update_docs
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os


class Command(BaseCommand):
    help = 'Update SciTeX documentation from repository'

    def handle(self, *args, **options):
        scitex_path = '/home/ywatanabe/proj/SciTeX-Code'
        docs_path = os.path.join(scitex_path, 'docs/RTD')
        
        self.stdout.write('Updating SciTeX repository...')
        
        # Pull latest changes
        result = subprocess.run(
            ['git', 'pull'], 
            cwd=scitex_path, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            self.stdout.write(
                self.style.ERROR(f'Git pull failed: {result.stderr}')
            )
            return
        
        self.stdout.write('Building documentation...')
        
        # Clean build
        result = subprocess.run(
            ['make', 'clean'], 
            cwd=docs_path, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            self.stdout.write(
                self.style.ERROR(f'Make clean failed: {result.stderr}')
            )
            return
        
        # Build HTML
        result = subprocess.run(
            ['make', 'html'], 
            cwd=docs_path, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            self.stdout.write(
                self.style.ERROR(f'Make html failed: {result.stderr}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('Documentation updated successfully!')
        )
        
        # Show build location
        build_path = os.path.join(docs_path, '_build/html')
        self.stdout.write(f'Documentation built at: {build_path}')