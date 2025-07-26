#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 16:28:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_Config.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_Config.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Configuration management for SciTeX Scholar.

Provides centralized configuration with environment variable support
and sensible defaults.

Priority order for configuration values:
1. Direct parameter specification (highest priority)
2. Configuration file (YAML)
3. Environment variables (SCITEX_* prefix)
4. Default values (lowest priority)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, Union
import yaml


@dataclass
class ScholarConfig:
    """
    Configuration for Scholar module.
    
    All parameters can be set via environment variables (SCITEX_SCHOLAR_* prefix)
    or passed directly.
    
    Priority order:
    1. Direct parameter specification (highest priority)
    2. Configuration file (YAML)
    3. Environment variables (SCITEX_SCHOLAR_* prefix)
    4. Default values (lowest priority)
    
    Example:
        # Using environment variables
        config = ScholarConfig()
        
        # Using direct parameters
        config = ScholarConfig(
            semantic_scholar_api_key="your-key",
            enable_auto_enrich=False
        )
        
        # Pass to Scholar
        scholar = Scholar(config=config)
    """
    
    # API Keys
    semantic_scholar_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_API_KEY")
    )
    crossref_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_CROSSREF_API_KEY")
    )
    
    # Email addresses for API access
    pubmed_email: str = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_PUBMED_EMAIL", "research@example.com")
    )
    crossref_email: str = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_CROSSREF_EMAIL", "research@example.com")
    )
    
    # Feature toggles
    enable_auto_enrich: bool = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_AUTO_ENRICH", "true").lower() == "true"
    )
    use_impact_factor_package: bool = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_USE_IMPACT_FACTOR_PACKAGE", "true").lower() == "true"
    )
    enable_auto_download: bool = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_AUTO_DOWNLOAD", "false").lower() == "true"
    )
    acknowledge_scihub_ethical_usage: bool = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_ACKNOWLEDGE_SCIHUB_ETHICAL_USAGE", "false").lower() == "true"
    )
    
    # Search configuration
    default_search_sources: list = field(
        default_factory=lambda: ["pubmed", "semantic_scholar", "google_scholar", "crossref", "arxiv"]
    )
    default_search_limit: int = 20
    
    # PDF management
    pdf_dir: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_PDF_DIR")
    )
    enable_pdf_extraction: bool = True
    
    # Performance settings
    max_parallel_requests: int = 3
    request_timeout: int = 30
    cache_size: int = 1000
    google_scholar_timeout: int = field(
        default_factory=lambda: int(os.getenv("SCITEX_SCHOLAR_GOOGLE_SCHOLAR_TIMEOUT", "10"))
    )
    
    # Advanced settings
    verify_ssl: bool = True
    debug_mode: bool = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_DEBUG_MODE", "false").lower() == "true"
    )
    
    # OpenAthens authentication
    openathens_enabled: bool = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_OPENATHENS_ENABLED", "false").lower() == "true"
    )
    openathens_org_id: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_OPENATHENS_ORG_ID")
    )
    openathens_idp_url: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_OPENATHENS_IDP_URL")
    )
    openathens_email: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    openathens_username: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_OPENATHENS_USERNAME")  # Deprecated
    )
    openathens_password: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD")  # Deprecated
    )
    openathens_institution_name: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_OPENATHENS_INSTITUTION_NAME")
    )
# Lean Library browser extension support
    use_lean_library: bool = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_USE_LEAN_LIBRARY", "true").lower() == "true"
    )
    lean_library_browser_profile: Optional[str] = field(
        default_factory=lambda: os.getenv("SCITEX_SCHOLAR_LEAN_LIBRARY_BROWSER_PROFILE")
    )
    user_agent: str = "SciTeX-Scholar/1.0"  # HTTP User-Agent for API requests
    
    # OpenURL resolver for institutional access
    openurl_resolver: str = field(
        default="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    )
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Expand paths if they contain ~ or environment variables
        if self.pdf_dir and isinstance(self.pdf_dir, str):
            self.pdf_dir = str(Path(self.pdf_dir).expanduser())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "semantic_scholar_api_key": self.semantic_scholar_api_key,
            "crossref_api_key": self.crossref_api_key,
            "pubmed_email": self.pubmed_email,
            "crossref_email": self.crossref_email,
            "enable_auto_enrich": self.enable_auto_enrich,
            "use_impact_factor_package": self.use_impact_factor_package,
            "enable_auto_download": self.enable_auto_download,
            "acknowledge_scihub_ethical_usage": self.acknowledge_scihub_ethical_usage,
            "default_search_sources": self.default_search_sources,
            "default_search_limit": self.default_search_limit,
            "pdf_dir": self.pdf_dir,
            "enable_pdf_extraction": self.enable_pdf_extraction,
            "max_parallel_requests": self.max_parallel_requests,
            "request_timeout": self.request_timeout,
            "cache_size": self.cache_size,
            "verify_ssl": self.verify_ssl,
            "use_lean_library": self.use_lean_library,
            "lean_library_browser_profile": self.lean_library_browser_profile,
            "user_agent": self.user_agent,
            "openurl_resolver": self.openurl_resolver,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScholarConfig":
        """Create configuration from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "ScholarConfig":
        """Load configuration from YAML file.
        
        Example YAML file:
            # ~/.scitex/scholar/config.yaml
            semantic_scholar_api_key: "your-key-here"
            pubmed_email: "your.email@example.com"
            enable_auto_enrich: true
            use_impact_factor_package: true
            enable_auto_download: false
            acknowledge_scihub_ethical_usage: false
            default_search_sources:
              - pubmed
              - arxiv
            pdf_dir: "~/.scitex/scholar/pdfs"
        """
        path = Path(path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls.from_dict(data)
    
    def to_yaml(self, path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        path = Path(path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and remove None values
        data = {k: v for k, v in self.to_dict().items() if v is not None}
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def load(cls, path: Optional[Union[str, Path]] = None) -> "ScholarConfig":
        """Load configuration from file or environment.
        
        Args:
            path: Path to YAML config file. If None, checks:
                  1. SCITEX_SCHOLAR_CONFIG environment variable
                  2. ~/.scitex/scholar/config.yaml
                  3. ./scholar_config.yaml
                  4. Falls back to environment variables
        """
        if path:
            return cls.from_yaml(path)
        
        # Check environment variable for config path
        env_path = os.getenv("SCITEX_SCHOLAR_CONFIG")
        if env_path and Path(env_path).exists():
            return cls.from_yaml(env_path)
        
        # Check default locations
        default_paths = [
            Path("~/.scitex/scholar/config.yaml").expanduser(),
            Path("./scholar_config.yaml"),
            Path("./.scitex_scholar.yaml"),
        ]
        
        for default_path in default_paths:
            if default_path.exists():
                return cls.from_yaml(default_path)
        
        # Fall back to environment variables
        return cls()
    
    def merge(self, **kwargs) -> "ScholarConfig":
        """Create new config with merged values."""
        current = self.to_dict()
        current.update(kwargs)
        return self.from_dict(current)
    
    @classmethod
    def show_env_vars(cls) -> str:
        """Show all environment variables and their current values."""
        env_vars = {
            "SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_API_KEY": "API key for Semantic Scholar",
            "SCITEX_SCHOLAR_CROSSREF_API_KEY": "API key for CrossRef",
            "SCITEX_SCHOLAR_PUBMED_EMAIL": "Email for PubMed API (default: research@example.com)",
            "SCITEX_SCHOLAR_CROSSREF_EMAIL": "Email for CrossRef API (default: research@example.com)",
            "SCITEX_SCHOLAR_AUTO_ENRICH": "Auto-enrich papers with citations/impact factors (default: true)",
            "SCITEX_SCHOLAR_USE_IMPACT_FACTOR_PACKAGE": "Use impact_factor package for journal metrics (default: true)",
            "SCITEX_SCHOLAR_AUTO_DOWNLOAD": "Auto-download open-access PDFs (default: false)",
            "SCITEX_SCHOLAR_ACKNOWLEDGE_SCIHUB_ETHICAL_USAGE": "Acknowledge ethical usage terms for Sci-Hub access (default: false)",
            "SCITEX_SCHOLAR_PDF_DIR": "Directory for storing PDFs",
            "SCITEX_SCHOLAR_CONFIG": "Path to config file",
        }
        
        output = ["Environment Variables for SciTeX Scholar:"]
        output.append("-" * 80)
        
        for var, desc in env_vars.items():
            value = os.getenv(var)
            if value and "API_KEY" in var:
                # Mask API keys for security
                value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            elif value is None:
                value = "<not set>"
            
            output.append(f"{var}")
            output.append(f"  Description: {desc}")
            output.append(f"  Current value: {value}")
            output.append("")
        
        return "\n".join(output)
    
    def show_config(self) -> str:
        """Show current configuration with sources."""
        output = ["Current SciTeX Scholar Configuration:"]
        output.append("-" * 80)
        
        # Map fields to their environment variable names
        field_to_env = {
            "semantic_scholar_api_key": "SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_API_KEY",
            "crossref_api_key": "SCITEX_SCHOLAR_CROSSREF_API_KEY",
            "pubmed_email": "SCITEX_SCHOLAR_PUBMED_EMAIL",
            "crossref_email": "SCITEX_SCHOLAR_CROSSREF_EMAIL",
            "enable_auto_enrich": "SCITEX_SCHOLAR_AUTO_ENRICH",
            "use_impact_factor_package": "SCITEX_SCHOLAR_USE_IMPACT_FACTOR_PACKAGE",
            "enable_auto_download": "SCITEX_SCHOLAR_AUTO_DOWNLOAD",
            "acknowledge_scihub_ethical_usage": "SCITEX_SCHOLAR_ACKNOWLEDGE_SCIHUB_ETHICAL_USAGE",
            "pdf_dir": "SCITEX_SCHOLAR_PDF_DIR",
        }
        
        config_dict = self.to_dict()
        
        for field, value in config_dict.items():
            # Mask sensitive values
            display_value = value
            if value and "api_key" in field and isinstance(value, str):
                display_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            
            output.append(f"{field}: {display_value}")
            
            # Show environment variable if applicable
            if field in field_to_env:
                env_var = field_to_env[field]
                env_value = os.getenv(env_var)
                if env_value:
                    output.append(f"  (from environment: {env_var})")
            
        return "\n".join(output)
    
    def show_secure_config(self) -> str:
        """
        Display configuration with sensitive data masked.
        
        Returns:
            Formatted string with configuration details (sensitive data masked)
        """
        def mask_value(value: Any, field_name: str) -> str:
            """Mask sensitive values based on field type."""
            if value is None:
                return "Not set"
            
            # API keys
            if "api_key" in field_name.lower():
                if len(str(value)) > 8:
                    return f"{str(value)[:4]}{'*' * (len(str(value)) - 8)}{str(value)[-4:]}"
                else:
                    return "*" * len(str(value))
            
            # Emails
            elif "email" in field_name.lower():
                parts = str(value).split('@')
                if len(parts) == 2:
                    user_part = parts[0]
                    if len(user_part) > 2:
                        masked_user = f"{user_part[:2]}{'*' * (len(user_part) - 2)}"
                    else:
                        masked_user = "*" * len(user_part)
                    return f"{masked_user}@{parts[1]}"
                else:
                    return "*" * len(str(value))
            
            # Paths (show only last directory)
            elif "dir" in field_name.lower() or "path" in field_name.lower():
                path_str = str(value)
                if '/' in path_str:
                    parts = path_str.split('/')
                    return f".../{'/'.join(parts[-2:])}" if len(parts) > 2 else path_str
                return path_str
            
            # Everything else
            else:
                return str(value)
        
        lines = []
        lines.append("=== SciTeX Scholar Configuration (Secure View) ===\n")
        
        # Group configurations
        api_keys = ["semantic_scholar_api_key", "crossref_api_key", "pubmed_email", "crossref_email"]
        features = ["enable_auto_enrich", "use_impact_factor_package", "enable_auto_download", 
                   "acknowledge_scihub_ethical_usage"]
        settings = ["pdf_dir", "default_search_limit", "default_search_sources", "max_parallel_requests"]
        
        # API Keys section
        lines.append("📚 API Keys & Credentials:")
        for field in api_keys:
            value = getattr(self, field)
            masked = mask_value(value, field)
            status = "✓" if value else "✗"
            lines.append(f"  {status} {field}: {masked}")
        
        # Features section
        lines.append("\n⚙️  Features:")
        for field in features:
            value = getattr(self, field)
            status = "✓ Enabled" if value else "✗ Disabled"
            lines.append(f"  • {field}: {status}")
        
        # Settings section
        lines.append("\n📁 Settings:")
        for field in settings:
            value = getattr(self, field)
            if isinstance(value, list):
                value_str = ", ".join(value)
            else:
                value_str = mask_value(value, field)
            lines.append(f"  • {field}: {value_str}")
        
        lines.append("\n" + "=" * 45)
        
        return "\n".join(lines)


# Default configuration instance
DEFAULT_CONFIG = ScholarConfig()

# EOF