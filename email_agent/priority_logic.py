from typing import Dict, Any, Optional

from .models import Priority
from .config import MODEL_PATH
from .utils.logging_utils import get_logger

logger = get_logger(__name__)

_MODEL = None  # lazy-loaded scikit-learn pipeline


def _load_model_if_needed() -> None:
    """
    Lazy-load the ML model from disk, if present.
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
        logger.info("Loaded email priority model from %s", MODEL_PATH)
    except Exception:
        logger.exception("Failed to load trained model from %s; using fallback.", MODEL_PATH)
        _MODEL = None


def _rule_based_classify(text: str) -> Dict[str, Any]:
    """
    Simple keyword-based classifier used as a fallback and baseline.
    """
    if text is None:
        text = ""
    lower = text.lower()

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

    return {
        "priority": priority,
        "confidence": confidence,
        "explanation": explanation,
        "raw_text_length": len(text),
    }


def classify_email(
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    context: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Top-level function used by app.py to classify an email.

    Behaviour:
    1. Try to use the trained scikit-learn model (if available).
    2. If the model is missing or fails, fall back to rule-based classification.
    """
    if text is None:
        text = ""

    # Try ML model first
    _load_model_if_needed()

    if _MODEL is not None:
        try:
            # _MODEL is a Pipeline: [TfidfVectorizer, LogisticRegression]
            y_pred = _MODEL.predict([text])[0]

            # Try to get a confidence score if predict_proba is available
            confidence = 0.8
            if hasattr(_MODEL, "predict_proba"):
                proba = _MODEL.predict_proba([text])[0]
                confidence = float(max(proba))

            priority = str(y_pred)  # expected to be "high" / "medium" / "low"
            explanation = "Predicted by trained ML model."

            result: Dict[str, Any] = {
                "priority": priority,
                "confidence": confidence,
                "explanation": explanation,
                "raw_text_length": len(text),
            }

            if metadata:
                result["metadata_used"] = list(metadata.keys())

            return result

        except Exception:
            logger.exception("ML model failed during classification; falling back to rules.")

    # Fallback: rule-based classification
    result = _rule_based_classify(text)
    if metadata:
        result["metadata_used"] = list(metadata.keys())
    return result
