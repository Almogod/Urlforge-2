import os
import pytest
from src.utils.security import is_safe_url, is_safe_path

def test_is_safe_url():
    # Public URLs
    assert is_safe_url("https://www.google.com") == True
    assert is_safe_url("http://example.com") == True
    
    # Local/Internal IPs
    assert is_safe_url("http://127.0.0.1") == False
    assert is_safe_url("http://localhost") == False
    assert is_safe_url("http://192.168.1.1") == False
    assert is_safe_url("http://10.0.0.1") == False
    assert is_safe_url("http://172.16.0.1") == False
    
    # Invalid schemes
    assert is_safe_url("file:///etc/passwd") == False
    assert is_safe_url("ftp://example.com") == False
    
    # Malformed URLs
    assert is_safe_url("not-a-url") == False
    assert is_safe_url("") == False

def test_is_safe_path():
    base_dir = os.path.abspath("test_dir")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    # Safe paths
    assert is_safe_path("file.txt", base_dir) == True
    assert is_safe_path("subdir/file.txt", base_dir) == True
    assert is_safe_path("./file.txt", base_dir) == True
    
    # Path traversal attempts
    assert is_safe_path("../etc/passwd", base_dir) == False
    assert is_safe_path("subdir/../../etc/passwd", base_dir) == False
    assert is_safe_path("/absolute/path", base_dir) == False
    
    # Clean up
    import shutil
    shutil.rmtree(base_dir)
