import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any

from .config import LTM_DIR, LTM_INDEX_PATH, LTM_RECORDS_DIR
from .utils.logging_utils import get_logger

logger = get_logger(__name__)


def _ensure_dirs() -> None:
    """
    Ensure LTM directories and index file exist.
    Safe to call multiple times.
    """
    LTM_DIR.mkdir(parents=True, exist_ok=True)
    LTM_RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    if not LTM_INDEX_PATH.exists():
        LTM_INDEX_PATH.write_text("{}", encoding="utf-8")


def _load_index() -> Dict[str, str]:
    _ensure_dirs()
    try:
        text = LTM_INDEX_PATH.read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        logger.exception("Failed to read LTM index file; resetting to empty.")
        return {}


def _save_index(index: Dict[str, str]) -> None:
    try:
        LTM_INDEX_PATH.write_text(json.dumps(index), encoding="utf-8")
    except Exception:
        logger.exception("Failed to write LTM index file.")


def _key_to_filename(task_key: str) -> str:
    """
    Convert a task key to a stable filename using a hash.
    """
    digest = hashlib.sha256(task_key.encode("utf-8")).hexdigest()
    return f"{digest}.json"


def lookup(task_key: str) -> Optional[Dict[str, Any]]:
    """
    Look up a cached result from LTM based on the task key.

    Returns:
        - dict with cached "output" payload if found
        - None if not found or on error
    """
    index = _load_index()
    filename = index.get(task_key)
    if not filename:
        return None

    record_path: Path = LTM_RECORDS_DIR / filename
    if not record_path.exists():
        return None

    try:
        text = record_path.read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        logger.exception("Failed to read LTM record: %s", record_path)
        return None


def store(task_key: str, result: Dict[str, Any]) -> None:
    """
    Store a result in LTM under the given task key.

    Failures are logged but do not raise exceptions,
    so the main agent flow can continue.
    """
    index = _load_index()
    filename = index.get(task_key) or _key_to_filename(task_key)
    record_path: Path = LTM_RECORDS_DIR / filename

    try:
        record_path.write_text(json.dumps(result), encoding="utf-8")
        index[task_key] = filename
        _save_index(index)
    except Exception:
        logger.exception("Failed to write LTM record: %s", record_path)
