#!/usr/bin/env python3
"""Debug config resolution for SSO credentials."""

import os
from src.scitex.scholar.config import ScholarConfig

def debug_config():
    print("=== Environment Variables ===")
    print(f"UNIMELB_SSO_USERNAME: '{os.getenv('UNIMELB_SSO_USERNAME', 'NOT_SET')}'")
    print(f"UNIMELB_SSO_PASSWORD: {'SET' if os.getenv('UNIMELB_SSO_PASSWORD') else 'NOT_SET'}")
    print()
    
    print("=== ScholarConfig Resolution ===")
    config = ScholarConfig()
    
    username = config.resolve("sso_username", default="")
    password = config.resolve("sso_password", default="", mask="****")
    
    print(f"Resolved username: '{username}'")
    print(f"Resolved password: '{password}'")
    print()
    
    print("=== Resolution Log ===")
    config.print_resolutions()

if __name__ == "__main__":
    debug_config()