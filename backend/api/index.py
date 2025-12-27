"""
Vercel serverless entrypoint
"""

from app import create_app

app = create_app()
