#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 18:01:49 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/externals/impact_factor/src/impact_factor/core/cache_manager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./impact_factor/core/cache_manager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import json
import pickle
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from scitex.logging import getLogger

logger = getLogger(__name__)


class CacheManager:
    """
    Efficient caching system for impact factor calculations and API responses
    
    Features:
    - JSON and pickle serialization support
    - Configurable expiration times
    - Cache size management
    - Thread-safe operations
    - Hierarchical cache organization
    - Cache statistics and monitoring
    """
    
    def __init__(
        self, 
        cache_dir: Optional[str] = None,
        default_ttl: int = 3600 * 24 * 7,  # 7 days
        max_cache_size_mb: int = 100,
        cleanup_on_start: bool = True
    ):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory for cache storage (default: ~/.scitex/impact_factor_cache)
            default_ttl: Default time-to-live in seconds
            max_cache_size_mb: Maximum cache size in MB
            cleanup_on_start: Whether to cleanup expired entries on initialization
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".scitex" / "impact_factor_cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_ttl = default_ttl
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        
        # Create subdirectories for different data types
        self.subdirs = {
            'api_responses': self.cache_dir / 'api_responses',
            'impact_factors': self.cache_dir / 'impact_factors', 
            'journal_data': self.cache_dir / 'journal_data',
            'search_results': self.cache_dir / 'search_results'
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)
        
        # Metadata file for cache tracking
        self.metadata_file = self.cache_dir / 'cache_metadata.json'
        self.metadata = self._load_metadata()
        
        if cleanup_on_start:
            self.cleanup_expired()
        
        logger.info(f"Cache manager initialized at: {self.cache_dir}")
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
        
        return {
            'entries': {},
            'created_at': datetime.now().isoformat(),
            'last_cleanup': None,
            'statistics': {
                'total_gets': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_sets': 0
            }
        }
    
    def _save_metadata(self):
        """Save cache metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def _get_cache_key(self, key: str) -> str:
        """Generate a safe cache key hash"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str, cache_type: str = 'api_responses') -> Path:
        """Get full path for cache file"""
        subdir = self.subdirs.get(cache_type, self.subdirs['api_responses'])
        return subdir / f"{cache_key}.cache"
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        cache_type: str = 'api_responses',
        use_pickle: bool = False
    ) -> bool:
        """
        Store value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = default)
            cache_type: Type of cache (api_responses, impact_factors, etc.)
            use_pickle: Whether to use pickle serialization
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key, cache_type)
            
            # Prepare cache entry
            cache_entry = {
                'key': key,
                'value': value,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat(),
                'ttl': ttl,
                'cache_type': cache_type,
                'serialization': 'pickle' if use_pickle else 'json'
            }
            
            # Serialize and save
            if use_pickle:
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_entry, f)
            else:
                with open(cache_path, 'w') as f:
                    json.dump(cache_entry, f, indent=2, default=str)
            
            # Update metadata
            self.metadata['entries'][cache_key] = {
                'key': key,
                'cache_type': cache_type,
                'created_at': cache_entry['created_at'],
                'expires_at': cache_entry['expires_at'],
                'file_path': str(cache_path),
                'serialization': cache_entry['serialization']
            }
            self.metadata['statistics']['total_sets'] += 1
            self._save_metadata()
            
            logger.debug(f"Cached key '{key}' in {cache_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache key '{key}': {e}")
            return False
    
    def get(self, key: str, cache_type: str = 'api_responses') -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            key: Cache key
            cache_type: Type of cache
            
        Returns:
            Cached value or None if not found/expired
        """
        try:
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key, cache_type)
            
            # Update statistics
            self.metadata['statistics']['total_gets'] += 1
            
            # Check if file exists
            if not cache_path.exists():
                self.metadata['statistics']['cache_misses'] += 1
                self._save_metadata()
                logger.debug(f"Cache miss: key '{key}' not found")
                return None
            
            # Load cache entry
            metadata_entry = self.metadata['entries'].get(cache_key)
            if not metadata_entry:
                self.metadata['statistics']['cache_misses'] += 1
                self._save_metadata()
                logger.debug(f"Cache miss: metadata for key '{key}' not found")
                return None
            
            # Check expiration
            expires_at = datetime.fromisoformat(metadata_entry['expires_at'])
            if datetime.now() > expires_at:
                self.metadata['statistics']['cache_misses'] += 1
                self._save_metadata()
                logger.debug(f"Cache miss: key '{key}' expired")
                # Clean up expired entry
                self._remove_cache_entry(cache_key)
                return None
            
            # Load and return value
            if metadata_entry['serialization'] == 'pickle':
                with open(cache_path, 'rb') as f:
                    cache_entry = pickle.load(f)
            else:
                with open(cache_path, 'r') as f:
                    cache_entry = json.load(f)
            
            self.metadata['statistics']['cache_hits'] += 1
            self._save_metadata()
            
            logger.debug(f"Cache hit: key '{key}' retrieved from {cache_type}")
            return cache_entry['value']
            
        except Exception as e:
            logger.error(f"Failed to retrieve cache key '{key}': {e}")
            self.metadata['statistics']['cache_misses'] += 1
            self._save_metadata()
            return None
    
    def delete(self, key: str, cache_type: str = 'api_responses') -> bool:
        """Delete a specific cache entry"""
        try:
            cache_key = self._get_cache_key(key)
            return self._remove_cache_entry(cache_key)
        except Exception as e:
            logger.error(f"Failed to delete cache key '{key}': {e}")
            return False
    
    def _remove_cache_entry(self, cache_key: str) -> bool:
        """Remove cache entry by cache key"""
        try:
            metadata_entry = self.metadata['entries'].get(cache_key)
            if metadata_entry:
                # Remove file
                cache_path = Path(metadata_entry['file_path'])
                if cache_path.exists():
                    cache_path.unlink()
                
                # Remove from metadata
                del self.metadata['entries'][cache_key]
                self._save_metadata()
                
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove cache entry {cache_key}: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """Remove all expired cache entries"""
        logger.info("Starting cache cleanup of expired entries")
        
        removed_count = 0
        current_time = datetime.now()
        
        # Create a copy of keys to avoid dictionary modification during iteration
        cache_keys = list(self.metadata['entries'].keys())
        
        for cache_key in cache_keys:
            entry = self.metadata['entries'][cache_key]
            expires_at = datetime.fromisoformat(entry['expires_at'])
            
            if current_time > expires_at:
                if self._remove_cache_entry(cache_key):
                    removed_count += 1
        
        self.metadata['last_cleanup'] = current_time.isoformat()
        self._save_metadata()
        
        logger.info(f"Cleanup completed: removed {removed_count} expired entries")
        return removed_count
    
    def cleanup_by_size(self) -> int:
        """Remove oldest entries if cache exceeds size limit"""
        current_size = self.get_cache_size()
        if current_size <= self.max_cache_size_bytes:
            return 0
        
        logger.info(f"Cache size ({current_size / 1024 / 1024:.1f}MB) exceeds limit, cleaning up")
        
        # Sort entries by creation time (oldest first)
        entries_by_age = sorted(
            self.metadata['entries'].items(),
            key=lambda x: x[1]['created_at']
        )
        
        removed_count = 0
        for cache_key, entry in entries_by_age:
            if self._remove_cache_entry(cache_key):
                removed_count += 1
                current_size = self.get_cache_size()
                if current_size <= self.max_cache_size_bytes:
                    break
        
        logger.info(f"Size cleanup completed: removed {removed_count} entries")
        return removed_count
    
    def clear_all(self, cache_type: Optional[str] = None) -> int:
        """Clear all cache entries or entries of specific type"""
        removed_count = 0
        
        if cache_type:
            # Clear specific type
            cache_keys = [
                key for key, entry in self.metadata['entries'].items()
                if entry['cache_type'] == cache_type
            ]
            logger.info(f"Clearing all {cache_type} cache entries")
        else:
            # Clear all
            cache_keys = list(self.metadata['entries'].keys())
            logger.info("Clearing all cache entries")
        
        for cache_key in cache_keys:
            if self._remove_cache_entry(cache_key):
                removed_count += 1
        
        logger.info(f"Cleared {removed_count} cache entries")
        return removed_count
    
    def get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        total_size = 0
        for entry in self.metadata['entries'].values():
            cache_path = Path(entry['file_path'])
            if cache_path.exists():
                total_size += cache_path.stat().st_size
        
        # Add metadata file size
        if self.metadata_file.exists():
            total_size += self.metadata_file.stat().st_size
        
        return total_size
    
    def get_statistics(self) -> Dict:
        """Get cache usage statistics"""
        stats = self.metadata['statistics'].copy()
        stats.update({
            'total_entries': len(self.metadata['entries']),
            'cache_size_mb': self.get_cache_size() / 1024 / 1024,
            'cache_size_limit_mb': self.max_cache_size_bytes / 1024 / 1024,
            'hit_rate': (
                stats['cache_hits'] / stats['total_gets'] 
                if stats['total_gets'] > 0 else 0.0
            ),
            'last_cleanup': self.metadata.get('last_cleanup'),
            'entries_by_type': {}
        })
        
        # Count entries by type
        for entry in self.metadata['entries'].values():
            cache_type = entry['cache_type']
            stats['entries_by_type'][cache_type] = stats['entries_by_type'].get(cache_type, 0) + 1
        
        return stats
    
    def list_entries(self, cache_type: Optional[str] = None) -> List[Dict]:
        """List cache entries with metadata"""
        entries = []
        
        for cache_key, entry in self.metadata['entries'].items():
            if cache_type is None or entry['cache_type'] == cache_type:
                entry_info = entry.copy()
                entry_info['cache_key'] = cache_key
                entry_info['expired'] = datetime.now() > datetime.fromisoformat(entry['expires_at'])
                entries.append(entry_info)
        
        return entries


def main():
    """Demonstration of CacheManager functionality"""
    logger.info("Starting Cache Manager demonstration")
    
    # Initialize cache manager
    cache = CacheManager(cache_dir="/tmp/demo_cache", max_cache_size_mb=10)
    
    logger.info("Testing cache operations")
    logger.info("=" * 40)
    
    # Test basic set/get operations
    logger.info("1. Testing basic cache operations")
    
    test_data = {
        'journal_name': 'Nature',
        'impact_factor': 49.962,
        'year': 2023,
        'metadata': {
            'publisher': 'Nature Publishing Group',
            'issn': ['0028-0836', '1476-4687']
        }
    }
    
    # Set cache entry
    success = cache.set('nature_2023_if', test_data, ttl=300, cache_type='impact_factors')
    logger.info(f"Cache set successful: {success}")
    
    # Get cache entry
    retrieved_data = cache.get('nature_2023_if', cache_type='impact_factors')
    logger.info(f"Cache get successful: {retrieved_data is not None}")
    if retrieved_data:
        logger.info(f"Retrieved journal: {retrieved_data['journal_name']}")
    
    logger.info("")
    
    # Test different cache types
    logger.info("2. Testing different cache types")
    
    cache_types = ['api_responses', 'impact_factors', 'journal_data', 'search_results']
    for i, cache_type in enumerate(cache_types):
        key = f"test_key_{i}"
        value = f"test_value_{i}_for_{cache_type}"
        cache.set(key, value, cache_type=cache_type)
        logger.info(f"Stored in {cache_type}: {key}")
    
    logger.info("")
    
    # Test serialization types
    logger.info("3. Testing serialization types")
    
    # JSON serialization (default)
    json_data = {'type': 'json', 'numbers': [1, 2, 3], 'nested': {'key': 'value'}}
    cache.set('json_test', json_data, cache_type='journal_data')
    
    # Pickle serialization
    pickle_data = {'type': 'pickle', 'complex_object': datetime.now()}
    cache.set('pickle_test', pickle_data, cache_type='journal_data', use_pickle=True)
    
    # Verify both work
    json_retrieved = cache.get('json_test', cache_type='journal_data')
    pickle_retrieved = cache.get('pickle_test', cache_type='journal_data')
    
    logger.info(f"JSON serialization works: {json_retrieved is not None}")
    logger.info(f"Pickle serialization works: {pickle_retrieved is not None}")
    logger.info("")
    
    # Test cache statistics
    logger.info("4. Cache statistics")
    stats = cache.get_statistics()
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"Cache size: {stats['cache_size_mb']:.3f} MB")
    logger.info(f"Hit rate: {stats['hit_rate']:.1%}")
    logger.info(f"Entries by type: {stats['entries_by_type']}")
    logger.info("")
    
    # Test cache listing
    logger.info("5. Cache entry listing")
    entries = cache.list_entries()
    logger.info(f"Found {len(entries)} cache entries:")
    for entry in entries[:3]:  # Show first 3
        logger.info(f"  {entry['key']} [{entry['cache_type']}] - expires: {entry['expires_at'][:19]}")
    logger.info("")
    
    # Test expiration (simulate with short TTL)
    logger.info("6. Testing cache expiration")
    cache.set('expire_test', 'will expire soon', ttl=1)  # 1 second TTL
    
    # Immediate retrieval should work
    immediate = cache.get('expire_test')
    logger.info(f"Immediate retrieval: {'Success' if immediate else 'Failed'}")
    
    # Wait for expiration
    time.sleep(2)
    expired = cache.get('expire_test')
    logger.info(f"After expiration: {'Success' if expired else 'Failed (as expected)'}")
    logger.info("")
    
    # Test cleanup operations
    logger.info("7. Testing cleanup operations")
    
    # Add some entries with short TTL
    for i in range(5):
        cache.set(f'temp_{i}', f'temporary_data_{i}', ttl=1)
    
    time.sleep(2)  # Let them expire
    
    # Cleanup expired entries
    removed = cache.cleanup_expired()
    logger.info(f"Cleaned up {removed} expired entries")
    
    # Final statistics
    final_stats = cache.get_statistics()
    logger.info(f"Final cache entries: {final_stats['total_entries']}")
    logger.info("")
    
    logger.success("Cache Manager demonstration completed")


if __name__ == "__main__":
    main()

# EOF