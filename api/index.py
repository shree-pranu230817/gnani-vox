"""
Vercel Serverless Function Entry Point for GNANI VOX Flask Application.
This file IS the serverless function — Vercel calls `app` (the WSGI callable).
"""

import os
import sys

# Ensure root project directory is on sys.path so we can import app, config, etc.
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Also add the api/ directory itself
api_dir = os.path.dirname(__file__)
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from app import app
