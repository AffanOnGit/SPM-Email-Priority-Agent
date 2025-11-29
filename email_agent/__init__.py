"""
Email Priority Agent package.

Contains core logic used by the Flask app (app.py):
- config & paths
- handshake (request/response) schemas
- internal email/priority models
- core classification logic
- long-term memory (LTM) handling
- training & evaluation utilities
"""

from .config import AGENT_NAME

__all__ = ["AGENT_NAME"]
