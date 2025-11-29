from pathlib import Path
import shutil

from email_agent.config import LTM_DIR, LTM_INDEX_PATH, LTM_RECORDS_DIR
from email_agent.ltm_store import lookup, store


def setup_module(module):
    """
    Clean LTM directory before tests, so tests start from a blank slate.
    """
    if LTM_DIR.exists():
        shutil.rmtree(LTM_DIR, ignore_errors=True)


def test_ltm_store_and_lookup_roundtrip():
    task_key = "test.intent:some text"
    result = {"priority": "high", "confidence": 0.95, "explanation": "test"}

    # Ensure lookup returns None before storing
    assert lookup(task_key) is None

    # Store result
    store(task_key, result)

    # Check that index and record files were created
    assert LTM_DIR.exists()
    assert LTM_INDEX_PATH.exists()
    assert LTM_RECORDS_DIR.exists()
    assert any(LTM_RECORDS_DIR.iterdir()), "Expected at least one record file."

    # Lookup should now return the stored result
    loaded = lookup(task_key)
    assert loaded is not None
    assert loaded["priority"] == "high"
    assert loaded["confidence"] == 0.95
