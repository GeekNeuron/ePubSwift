# utils/helpers.py
import sys
import os
import re

def get_base_path():
    """Gets the correct base path, whether running from script or bundled exe."""
    if getattr(sys, 'frozen', False):
        # We are running in a bundle
        return os.path.dirname(sys.executable)
    else:
        # We are running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

def is_rtl(text, threshold=0.4):
    """Detects if a text is predominantly Right-to-Left."""
    if not text: return False
    clean_text = re.sub('<[^<]+?>', '', text)
    if not clean_text: return False
    sample = clean_text[:500]
    if not sample: return False
    rtl_chars = len(re.findall(r'[\u0600-\u06FF]', sample))
    return (rtl_chars / len(sample)) > threshold
