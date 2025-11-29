# Save/load email_priority_model.pkl
from typing import Any

import joblib

from ..config import MODEL_PATH
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


def save_model(model: Any) -> None:
    """
    Save a trained model to disk.
    """
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    logger.info("Saved model to %s", MODEL_PATH)


def load_model() -> Any:
    """
    Load a trained model from disk.

    Raises FileNotFoundError if the model file does not exist.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No model file found at {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)
    logger.info("Loaded model from %s", MODEL_PATH)
    return model
