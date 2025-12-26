"""Vercel serverless function entry point."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import app

# Vercel expects 'app' at module level
