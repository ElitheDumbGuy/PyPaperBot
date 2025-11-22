import os
import sys
import warnings

def install():
    """
    Install suppression for annoying but harmless Selenium/Chrome errors.
    """
    # Suppress DeprecationWarnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Redirect stderr to devnull ONLY for the specific OSError from undetected_chromedriver
    # This is tricky because we don't want to hide real errors.
    # Instead, we can try to patch the library's __del__ method if possible, 
    # or just accept it on Windows. 
    
    # A better approach for Windows handle errors in __del__:
    if sys.platform == 'win32':
        try:
            import undetected_chromedriver as uc
            
            # Monkey patch the quit method to be safer
            original_quit = uc.Chrome.quit
            def safe_quit(self):
                try:
                    original_quit(self)
                except OSError:
                    pass
                except Exception:
                    pass
            
            uc.Chrome.quit = safe_quit
            
        except ImportError:
            pass
