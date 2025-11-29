from typing import Dict, Any, Optional

from .models import Priority
from .config import MODEL_PATH
from .utils.logging_utils import get_logger

logger = get_logger(__name__)

# Placeholder for a future loaded ML model (scikit-learn)
_MODEL = None


def _load_model_if_needed() -> None:
    """
    Lazy-load the ML model from disk, if present.
    For now, this is optional and can be left unimplemented
    until you train and save a real model.
    """
    global _MODEL
    if _MODEL is not None:
        return

    if not MODEL_PATH.exists():
        logger.info("No trained model found at %s; using rule-based fallback.", MODEL_PATH)
        return

    try:
        import joblib

        _MODEL = joblib.load(MODEL_PATH)
        logger.info("Loaded model from %s", MODEL_PATH)
    except Exception:
        logger.exception("Failed to load trained model from %s; using fallback.", MODEL_PATH)
        _MODEL = None


def classify_email(
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    context: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Top-level function used by app.py to classify an email.

    Current behaviour:
    - Uses a simple keyword rule-based classifier.
    - Later, you can:
      - Load the ML model via _load_model_if_needed()
      - Extract features from text/metadata
      - Predict priority via model
    """
    if text is None:
        text = ""
    lower = text.lower()

    # --- Simple rule-based fallback classifier ---

    if any(word in lower for word in ["urgent", "asap", "immediately", "deadline"]):
        priority = Priority.HIGH.value
        confidence = 0.90
        explanation = "Detected high-urgency keywords in the email text."
    elif any(word in lower for word in ["soon", "important", "priority"]):
        priority = Priority.MEDIUM.value
        confidence = 0.75
        explanation = "Detected medium-priority keywords in the email text."
    else:
        priority = Priority.LOW.value
        confidence = 0.60
        explanation = "No urgency keywords detected; defaulted to low priority."

    result: Dict[str, Any] = {
        "priority": priority,
        "confidence": confidence,
        "explanation": explanation,
        "raw_text_length": len(text),
    }

    # You can optionally add metadata/context echoes for debugging
    if metadata:
        result["metadata_used"] = list(metadata.keys())

    return result
