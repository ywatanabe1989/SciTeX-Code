#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 23:58:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/core/_ConfigurationResolver.py
# ----------------------------------------

"""Configuration resolution and validation for DOI resolution."""

from typing import Any, Dict, List, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class ConfigurationResolver:
    """Handles email resolution, source configuration, and validation.
    
    Responsibilities:
    - Email address resolution with fallback chain
    - Source list configuration and validation
    - Configuration parameter resolution
    - Default value handling and validation
    """

    # Default source order
    DEFAULT_SOURCES = ["url_extractor", "crossref", "semantic_scholar_enhanced", "pubmed", "openalex"]

    def __init__(self, config=None):
        """Initialize configuration resolver.
        
        Args:
            config: ScholarConfig instance or None to create default
        """
        if config is None:
            from ...config import ScholarConfig
            config = ScholarConfig()
        
        self.config = config
        logger.debug("ConfigurationResolver initialized")

    def resolve_email_configuration(
        self,
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
    ) -> Dict[str, str]:
        """Resolve email addresses with proper fallbacks.
        
        Priority: direct param -> config -> environment -> default
        
        Args:
            email_crossref: Direct CrossRef email override
            email_pubmed: Direct PubMed email override
            email_openalex: Direct OpenAlex email override
            email_semantic_scholar: Direct Semantic Scholar email override
            email_arxiv: Direct ArXiv email override
            
        Returns:
            Dictionary mapping service names to resolved email addresses
        """
        email_config = {}
        
        # Resolve CrossRef email
        email_config["crossref"] = self.config.resolve(
            "crossref_email", email_crossref, "research@example.com", str
        )
        
        # Resolve PubMed email
        email_config["pubmed"] = self.config.resolve(
            "pubmed_email", email_pubmed, "research@example.com", str
        )
        
        # Resolve OpenAlex email
        email_config["openalex"] = self.config.resolve(
            "openalex_email", email_openalex, "research@example.com", str
        )
        
        # Resolve Semantic Scholar email
        email_config["semantic_scholar"] = self.config.resolve(
            "semantic_scholar_email",
            email_semantic_scholar,
            "research@example.com",
            str,
        )
        
        # Resolve ArXiv email
        email_config["arxiv"] = self.config.resolve(
            "arxiv_email", email_arxiv, "research@example.com", str
        )
        
        logger.debug(f"Resolved email configuration: {list(email_config.keys())}")
        return email_config

    def resolve_sources_configuration(self, sources: Optional[List[str]] = None) -> List[str]:
        """Resolve sources list with configuration fallbacks.
        
        Args:
            sources: Direct sources list override
            
        Returns:
            Resolved list of source names
        """
        resolved_sources = self.config.resolve(
            "doi_sources", sources, self.DEFAULT_SOURCES, list
        )
        
        logger.debug(f"Resolved sources configuration: {resolved_sources}")
        return resolved_sources

    def resolve_api_keys(self) -> Dict[str, Optional[str]]:
        """Resolve API keys for various services.
        
        Returns:
            Dictionary mapping service names to API keys (None if not configured)
        """
        api_keys = {}
        
        # Semantic Scholar API key
        api_keys["semantic_scholar"] = self.config.resolve(
            'semantic_scholar_api_key', None, None, str
        )
        
        # Add other API keys as needed
        # api_keys["crossref"] = self.config.resolve("crossref_api_key", None, None, str)
        
        logger.debug(f"Resolved API keys: {list(k for k, v in api_keys.items() if v is not None)}")
        return api_keys

    def resolve_project_configuration(self, project: Optional[str] = None) -> str:
        """Resolve project name for Scholar library storage.
        
        Args:
            project: Direct project name override
            
        Returns:
            Resolved project name
        """
        resolved_project = project or "master"
        logger.debug(f"Resolved project: {resolved_project}")
        return resolved_project

    def resolve_rate_limit_configuration(self) -> Dict[str, Any]:
        """Resolve rate limiting configuration.
        
        Returns:
            Dictionary with rate limiting configuration
        """
        rate_limit_config = {
            "state_file": self.config.path_manager.get_workspace_logs_dir() / "rate_limit_state.json",
            "default_delay": self.config.resolve("rate_limit_default_delay", None, 1.0, float),
            "adaptive_enabled": self.config.resolve("rate_limit_adaptive", None, True, bool),
            "max_retries": self.config.resolve("rate_limit_max_retries", None, 3, int),
        }
        
        logger.debug("Resolved rate limiting configuration")
        return rate_limit_config

    def create_enrichment_configuration(self, email_config: Dict[str, str], api_keys: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Create enrichment configuration for ResolutionOrchestrator.
        
        Args:
            email_config: Resolved email configuration
            api_keys: Resolved API keys
            
        Returns:
            Enrichment configuration dictionary
        """
        enrichment_config = {
            'email_crossref': email_config.get('crossref'),
            'email_pubmed': email_config.get('pubmed'),
            'email_openalex': email_config.get('openalex'),
            'email_semantic_scholar': email_config.get('semantic_scholar'),
            'semantic_scholar_api_key': api_keys.get('semantic_scholar')
        }
        
        logger.debug("Created enrichment configuration")
        return enrichment_config

    def validate_configuration(
        self,
        email_config: Dict[str, str],
        sources: List[str],
        project: str
    ) -> Dict[str, Any]:
        """Validate complete configuration and return validation results.
        
        Args:
            email_config: Email configuration to validate
            sources: Source list to validate
            project: Project name to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "email_validation": {},
            "sources_validation": {},
        }
        
        # Validate email addresses
        for service, email in email_config.items():
            if not email or email == "research@example.com":
                validation["warnings"].append(f"Using default email for {service}: {email}")
                validation["email_validation"][service] = "default"
            elif "@" not in email or "." not in email:
                validation["errors"].append(f"Invalid email format for {service}: {email}")
                validation["email_validation"][service] = "invalid"
                validation["valid"] = False
            else:
                validation["email_validation"][service] = "valid"
        
        # Validate sources
        if not sources:
            validation["errors"].append("No sources configured")
            validation["valid"] = False
        else:
            from ._SourceManager import SourceManager
            available_sources = SourceManager.SOURCE_CLASSES.keys()
            
            for source in sources:
                if source not in available_sources:
                    validation["errors"].append(f"Unknown source: {source}")
                    validation["sources_validation"][source] = "unknown"
                    validation["valid"] = False
                else:
                    validation["sources_validation"][source] = "valid"
        
        # Validate project name
        if not project or not project.strip():
            validation["warnings"].append("Empty project name, using 'master'")
        
        return validation

    def get_configuration_summary(
        self,
        email_config: Dict[str, str],
        sources: List[str],
        project: str,
        api_keys: Dict[str, Optional[str]]
    ) -> Dict[str, Any]:
        """Get a comprehensive configuration summary.
        
        Args:
            email_config: Resolved email configuration
            sources: Resolved sources list
            project: Resolved project name
            api_keys: Resolved API keys
            
        Returns:
            Configuration summary dictionary
        """
        return {
            "project": project,
            "sources": sources,
            "email_services": list(email_config.keys()),
            "api_keys_configured": [k for k, v in api_keys.items() if v is not None],
            "config_file": str(self.config.config_file) if hasattr(self.config, 'config_file') else None,
            "workspace_dir": str(self.config.path_manager.get_workspace_logs_dir()),
            "library_dir": str(self.config.path_manager.library_dir),
        }

    def resolve_all_configuration(
        self,
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
        sources: Optional[List[str]] = None,
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resolve all configuration in one call.
        
        Returns:
            Dictionary with all resolved configuration
        """
        # Resolve individual components
        email_config = self.resolve_email_configuration(
            email_crossref, email_pubmed, email_openalex, 
            email_semantic_scholar, email_arxiv
        )
        
        resolved_sources = self.resolve_sources_configuration(sources)
        resolved_project = self.resolve_project_configuration(project)
        api_keys = self.resolve_api_keys()
        rate_limit_config = self.resolve_rate_limit_configuration()
        enrichment_config = self.create_enrichment_configuration(email_config, api_keys)
        
        # Validate configuration
        validation = self.validate_configuration(email_config, resolved_sources, resolved_project)
        
        # Create summary
        summary = self.get_configuration_summary(email_config, resolved_sources, resolved_project, api_keys)
        
        return {
            "email_config": email_config,
            "sources": resolved_sources,
            "project": resolved_project,
            "api_keys": api_keys,
            "rate_limit_config": rate_limit_config,
            "enrichment_config": enrichment_config,
            "validation": validation,
            "summary": summary,
        }


if __name__ == "__main__":
    # Example usage
    resolver = ConfigurationResolver()
    
    # Test full configuration resolution
    config = resolver.resolve_all_configuration(
        email_crossref="test@example.com",
        sources=["crossref", "pubmed", "url_extractor"],
        project="test_project"
    )
    
    print("Configuration Resolution Test:")
    print(f"Email config: {config['email_config']}")
    print(f"Sources: {config['sources']}")
    print(f"Project: {config['project']}")
    print(f"Validation valid: {config['validation']['valid']}")
    
    if config['validation']['warnings']:
        print(f"Warnings: {config['validation']['warnings']}")
    
    if config['validation']['errors']:
        print(f"Errors: {config['validation']['errors']}")
    
    print(f"Summary: {config['summary']}")