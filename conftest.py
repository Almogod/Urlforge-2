"""Root conftest.py — ensures the project root is on sys.path so that
`from src.<module>` imports resolve correctly during pytest collection."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
