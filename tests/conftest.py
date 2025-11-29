import sys
from pathlib import Path

import pytest

# --- Ensure project root is on sys.path so "email_agent" & "app" can be imported ---

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app as flask_app  # import the Flask app instance from app.py


@pytest.fixture(scope="session")
def app():
    """
    Provide the Flask app object for tests.
    """
    return flask_app


@pytest.fixture(scope="session")
def client(app):
    """
    Flask test client for making requests to /health and /handle in tests.
    """
    return app.test_client()
