#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 20:36:50 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/session/_manager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/session/_manager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Session manager for tracking active experiment sessions."""

from datetime import datetime
from typing import Any, Dict


class SessionManager:
    """Manages experiment sessions with tracking and lifecycle management."""
    
    def __init__(self):
        self.active_sessions = {}
    
    def create_session(self, session_id: str, config: Dict[str, Any]) -> None:
        """Register a new session.
        
        Parameters
        ----------
        session_id : str
            Unique identifier for the session
        config : Dict[str, Any]
            Session configuration dictionary
        """
        self.active_sessions[session_id] = {
            'config': config,
            'start_time': datetime.now(),
            'status': 'running'
        }
    
    def close_session(self, session_id: str) -> None:
        """Mark a session as closed.
        
        Parameters
        ----------
        session_id : str
            Unique identifier for the session to close
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['status'] = 'closed'
            self.active_sessions[session_id]['end_time'] = datetime.now()
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """Get all active sessions.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary of active session information
        """
        return {k: v for k, v in self.active_sessions.items() if v['status'] == 'running'}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get specific session information.
        
        Parameters
        ----------
        session_id : str
            Session ID to retrieve
            
        Returns
        -------
        Dict[str, Any]
            Session information dictionary
        """
        return self.active_sessions.get(session_id, {})
    
    def list_sessions(self) -> Dict[str, Any]:
        """Get all sessions (active and closed).
        
        Returns
        -------
        Dict[str, Any]
            Dictionary of all session information
        """
        return self.active_sessions.copy()


# Global session manager
_session_manager = SessionManager()


def get_global_session_manager() -> SessionManager:
    """Get the global session manager instance.
    
    Returns
    -------
    SessionManager
        Global session manager instance
    """
    return _session_manager

# EOF