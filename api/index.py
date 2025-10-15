"""
Vercel serverless function entry point for Code Review Assistant
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and export the FastAPI app
from main import app