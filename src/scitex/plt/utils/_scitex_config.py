#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SciTeX Ecosystem Configuration Manager

"""
Unified configuration system for the complete SciTeX ecosystem:
SciTeX + SciTeX-Code + SciTeX-Paper + SigMacro + Emacs-Claude-Code integration
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import json


class SciTeXConfig:
    """Central configuration manager for the SciTeX ecosystem"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize SciTeX configuration
        
        Parameters
        ----------
        config_path : str, optional
            Path to configuration file. Defaults to ~/.scitex/config.yaml
        """
        self.config_path = config_path or os.path.expanduser("~/.scitex/config.yaml")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default SciTeX ecosystem configuration"""
        default_config = {
            'scitex_ecosystem': {
                'version': '1.0.0',
                'core_engine': 'claude_code',
                'emacs_integration': True,
                'auto_workflow': True
            },
            
            'paths': {
                'scitex_paper': '~/proj/SciTeX-Paper/',
                'scitex_code': '~/proj/SciTeX-Code/',
                'sigmacro': '~/proj/SigMacro/',
                'emacs_claude': '~/proj/emacs-claude-code/',
                'scitex_data': '~/data/',
                'output': '~/output/'
            },
            
            'scitex': {
                'auto_metadata': True,
                'yaml_export': True,
                'csv_export': True,
                'tracking_enabled': True,
                'default_journal': 'nature'
            },
            
            'ai_integration': {
                'claude_code_enabled': True,
                'auto_code_generation': True,
                'auto_manuscript_writing': True,
                'ai_assisted_analysis': True,
                'emacs_claude_integration': True
            },
            
            'publication': {
                'default_journal': 'nature',
                'auto_formatting': True,
                'latex_compilation': True,
                'submission_package': True,
                'reproducibility_level': 'full'
            },
            
            'workflow': {
                'auto_save_metadata': True,
                'auto_export_yaml': True,
                'auto_generate_methods': True,
                'auto_create_figures': True,
                'ai_quality_check': True
            }
        }
        
        # Create config directory and save
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        config_to_save = config or self.config
        with open(self.config_path, 'w') as f:
            yaml.dump(config_to_save, f, default_flow_style=False, sort_keys=False, indent=2)
    
    def get_scitex_paths(self) -> Dict[str, str]:
        """Get expanded SciTeX ecosystem paths"""
        paths = {}
        for key, path in self.config.get('paths', {}).items():
            paths[key] = os.path.expanduser(path)
        return paths
    
    def setup_scitex_directories(self):
        """Create SciTeX ecosystem directory structure"""
        paths = self.get_scitex_paths()
        
        # Create main directories
        for path_name, path in paths.items():
            os.makedirs(path, exist_ok=True)
            
        # Create SciTeX-Paper subdirectories
        scitex_paper = paths.get('scitex_paper')
        if scitex_paper:
            subdirs = ['figures', 'data', 'metadata', 'code', 'sections', 'manuscripts']
            for subdir in subdirs:
                os.makedirs(os.path.join(scitex_paper, subdir), exist_ok=True)
    
    def get_ai_settings(self) -> Dict[str, Any]:
        """Get AI integration settings"""
        return self.config.get('ai_integration', {})
    
    def get_publication_settings(self) -> Dict[str, Any]:
        """Get publication workflow settings"""
        return self.config.get('publication', {})
    
    def is_emacs_claude_enabled(self) -> bool:
        """Check if Emacs-Claude integration is enabled"""
        return self.config.get('ai_integration', {}).get('emacs_claude_integration', False)
    
    def get_default_journal(self) -> str:
        """Get default target journal"""
        return self.config.get('publication', {}).get('default_journal', 'nature')
    
    def enable_ai_workflow(self):
        """Enable full AI-powered workflow"""
        self.config['ai_integration']['claude_code_enabled'] = True
        self.config['ai_integration']['auto_code_generation'] = True
        self.config['ai_integration']['auto_manuscript_writing'] = True
        self.config['workflow']['ai_quality_check'] = True
        self.save_config()
    
    def create_project_config(self, project_name: str, project_path: str):
        """Create project-specific configuration"""
        project_config = {
            'project': {
                'name': project_name,
                'path': project_path,
                'created': str(pd.Timestamp.now()),
                'scitex_version': '1.0.0'
            },
            'inherit_from': self.config_path,
            'overrides': {
                'paths': {
                    'output': os.path.join(project_path, 'output'),
                    'data': os.path.join(project_path, 'data'),
                    'figures': os.path.join(project_path, 'figures')
                }
            }
        }
        
        project_config_path = os.path.join(project_path, '.scitex_project.yaml')
        with open(project_config_path, 'w') as f:
            yaml.dump(project_config, f, default_flow_style=False, indent=2)
        
        return project_config_path


# Global configuration instance
_scitex_config = None

def get_scitex_config() -> SciTeXConfig:
    """Get global SciTeX configuration instance"""
    global _scitex_config
    if _scitex_config is None:
        _scitex_config = SciTeXConfig()
    return _scitex_config


def configure_scitex_ecosystem():
    """Configure the complete SciTeX ecosystem"""
    config = get_scitex_config()
    
    print("🚀 Configuring SciTeX Ecosystem...")
    print("="*50)
    
    # Setup directories
    config.setup_scitex_directories()
    paths = config.get_scitex_paths()
    
    print("📁 Directory Structure:")
    for name, path in paths.items():
        status = "✅" if os.path.exists(path) else "❌"
        print(f"  {status} {name}: {path}")
    
    # Check AI integration
    print("\n🤖 AI Integration:")
    ai_settings = config.get_ai_settings()
    for setting, enabled in ai_settings.items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {setting}")
    
    # Check Emacs-Claude integration
    emacs_claude_path = paths.get('emacs_claude')
    if emacs_claude_path and os.path.exists(emacs_claude_path):
        print(f"\n💻 Emacs-Claude Integration: ✅ {emacs_claude_path}")
    else:
        print(f"\n💻 Emacs-Claude Integration: ❌ Not found")
    
    print(f"\n📋 Configuration saved: {config.config_path}")
    print("\n🎯 SciTeX Ecosystem Ready!")
    
    return config


if __name__ == "__main__":
    # Setup the complete ecosystem
    configure_scitex_ecosystem()