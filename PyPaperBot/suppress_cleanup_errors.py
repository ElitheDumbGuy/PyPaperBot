# -*- coding: utf-8 -*-
"""
Suppress cleanup errors from undetected_chromedriver on Windows.
This module filters stderr to remove Chrome driver cleanup errors.
"""

import sys
import os

class _StderrFilter:
    """Filter for stderr that suppresses Chrome driver cleanup errors."""
    
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.suppress_next_lines = 0
        
    def write(self, text):
        """Write to stderr, filtering out Chrome cleanup errors."""
        # If we're in suppression mode, count down
        if self.suppress_next_lines > 0:
            self.suppress_next_lines -= 1
            return len(text)
        
        # Check for the start of Chrome cleanup error
        if 'Exception ignored in:' in text:
            self.suppress_next_lines = 15  # Suppress next 15 lines (the whole traceback)
            return len(text)
        
        # Check for Chrome-related errors
        if 'Chrome.__del__' in text or 'undetected_chromedriver' in text:
            return len(text)
        
        # Check for WinError 6 specifically
        if 'WinError 6' in text or 'handle is invalid' in text or 'OSError' in text:
            return len(text)
        
        # Write everything else normally
        try:
            return self.original_stderr.write(text)
        except:
            return len(text)
    
    def flush(self):
        """Flush the original stderr."""
        try:
            self.original_stderr.flush()
        except:
            pass
    
    def __getattr__(self, name):
        """Delegate all other attributes to original stderr."""
        return getattr(self.original_stderr, name)

_original_stderr = None

def install():
    """Install the stderr filter."""
    global _original_stderr
    if _original_stderr is None:
        _original_stderr = sys.stderr
        sys.stderr = _StderrFilter(_original_stderr)

def uninstall():
    """Restore the original stderr."""
    global _original_stderr
    if _original_stderr is not None:
        sys.stderr = _original_stderr
        _original_stderr = None

