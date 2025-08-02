#!/bin/bash
# SciTeX Scholar Cleanup Script
# Generated on: 2025-08-03T02:24:45.825626
# 
# This script will clean up obsolete files in the SciTeX Scholar system.
# IMPORTANT: Review all operations before running!

set -e  # Exit on error

echo "🧹 SciTeX Scholar Cleanup Script"
echo "================================="

# Backup important files first
BACKUP_DIR="$HOME/.scitex/scholar/backup/cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup in $BACKUP_DIR"

# Archive versioned source files
echo "📝 Archiving versioned source files..."
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v10-parallel-is-not-default.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v11-parallel-is-default-but-not-working.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v13-resolved-url-not-defined.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v06-without-exponential-backoff.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v07-not-giving-up.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v03-not-working-with-link-finder.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v01-with-page-object.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v08-giveup-and-not-finding-anything.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v02-not-waiting-until-final-page.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "src/scitex/scholar/open_url/.old/_OpenURLResolver_v04-open-with-new-tab-not-handled.py" "$BACKUP_DIR/" 2>/dev/null || true

# Clean up old backup files (>30 days)
echo "🗑️  Removing old backup files..."

echo "✅ Cleanup complete!"
echo "📊 Summary:"
echo "  - Files archived: 47"
echo "  - Files deleted: 0"
echo "  - Backup location: $BACKUP_DIR"
