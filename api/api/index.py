"""Vercel serverless function entry point."""

from src.main import app

# Vercel expects 'app' or 'handler' at module level
handler = app
