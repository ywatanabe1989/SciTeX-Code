#!/bin/bash
# Kill Chrome SingletonLock processes to fix the ProcessSingleton error

echo "Checking for Chrome SingletonLock..."

# Find and remove SingletonLock files
SINGLETON_LOCKS=$(find ~/.config -name "SingletonLock" 2>/dev/null)

if [ ! -z "$SINGLETON_LOCKS" ]; then
    echo "Found SingletonLock files:"
    echo "$SINGLETON_LOCKS"
    echo
    echo "Removing SingletonLock files..."
    echo "$SINGLETON_LOCKS" | xargs rm -f
    echo "✓ Removed SingletonLock files"
else
    echo "No SingletonLock files found"
fi

# Check for running Chrome processes
CHROME_PROCS=$(pgrep -f "chrome.*--user-data-dir" | wc -l)

if [ $CHROME_PROCS -gt 0 ]; then
    echo
    echo "Found $CHROME_PROCS Chrome processes using user data directories"
    echo "You may want to close Chrome or run: pkill -f chrome"
fi

echo
echo "Done. Try running your script again."