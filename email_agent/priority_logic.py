from typing import Dict, Any, Optional, List

from .models import Priority
from .config import MODEL_PATH
from .utils.logging_utils import get_logger

logger = get_logger(__name__)

_MODEL = None  # lazy-loaded scikit-learn pipeline

# Simple keyword groups for explanation
URGENT_KEYWORDS = ["urgent", "asap", "immediately", "deadline", "critical", "today"]
MEDIUM_KEYWORDS = ["soon", "important", "priority", "reminder", "this week"]
CASUAL_KEYWORDS = ["memes", "photos", "fun", "joke", "newsletter"]

# Simple metadata-based signals
IMPORTANT_SENDER_HINTS = ["boss", "manager", "hod", "coordinator"]
IMPORTANT_SUBJECT_HINTS = ["exam", "deadline", "submission", "project", "meeting"]


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


def _find_keywords(text: str, keywords: List[str]) -> List[str]:
    lower = text.lower()
    return [kw for kw in keywords if kw in lower]


def _inspect_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Look at sender/subject and return simple signals we can mention in explanations.
    """
    signals: Dict[str, Any] = {
        "important_sender": False,
        "important_subject": False,
        "sender_match": None,
        "subject_match": None,
    }
    if not metadata:
        return signals

    sender = str(metadata.get("sender", "")).lower()
    subject = str(metadata.get("subject", "")).lower()

    for hint in IMPORTANT_SENDER_HINTS:
        if hint in sender:
            signals["important_sender"] = True
            signals["sender_match"] = hint
            break

    for hint in IMPORTANT_SUBJECT_HINTS:
        if hint in subject:
            signals["important_subject"] = True
            signals["subject_match"] = hint
            break

    return signals


def _build_explanation_from_signals(
    priority: str,
    confidence: float,
    text: str,
    used_model: bool,
    urgent_hits: List[str],
    medium_hits: List[str],
    casual_hits: List[str],
    meta_signals: Dict[str, Any],
) -> str:
    """
    Turn the raw signals into a human-readable explanation string.

    Requirements:
    - Do NOT use the word "Predicted".
    - Confidence score should appear at the END of the explanation.
    - Include a tag indicating whether ML model or rule-based logic was used.
    - Keep detected words/phrases in the explanation.
    """
    parts: List[str] = []

    # 1) Base line: where the decision came from (no "predicted")
    if used_model:
        parts.append(f"Priority classified as {priority.upper()} using the trained model.")
        tag = "[TAG: ML_MODEL]"
    else:
        parts.append(f"Priority classified as {priority.upper()} using rule-based heuristics.")
        tag = "[TAG: RULE_BASED]"

    # 2) Text-based signals
    if urgent_hits:
        parts.append(f"Detected high-urgency words in the text: {', '.join(urgent_hits)}.")
    elif medium_hits:
        parts.append(f"Detected medium-urgency words in the text: {', '.join(medium_hits)}.")
    elif casual_hits:
        parts.append(f"Detected casual/non-urgent words in the text: {', '.join(casual_hits)}.")

    # 3) Metadata-based signals
    if meta_signals.get("important_sender"):
        parts.append(
            "Sender appears important (matched hint: "
            f"{meta_signals.get('sender_match')})."
        )
    if meta_signals.get("important_subject"):
        parts.append(
            "Subject contains important hint: "
            f"{meta_signals.get('subject_match')}."
        )

    # 4) Fallback if nothing else was found
    if len(parts) == 1:
        # only base-line explanation so far
        parts.append("No specific urgency or metadata hints were detected in this email.")

    # Join all explanation parts, then append tag and confidence at the end
    explanation_core = " ".join(parts)

    # Confidence must be at the end of the explanation string
    explanation = f"{explanation_core} {tag} Confidence={confidence:.2f}."

    return explanation


def _rule_based_classify(text: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simple keyword-based classifier used as a fallback and baseline,
    but now with better explanations.
    """
    if text is None:
        text = ""
    lower = text.lower()

    urgent_hits = _find_keywords(lower, URGENT_KEYWORDS)
    medium_hits = _find_keywords(lower, MEDIUM_KEYWORDS)
    casual_hits = _find_keywords(lower, CASUAL_KEYWORDS)
    meta_signals = _inspect_metadata(metadata)

    # Decide priority
    if urgent_hits or meta_signals.get("important_subject") or meta_signals.get("important_sender"):
        priority = Priority.HIGH.value
        confidence = 0.90
    elif medium_hits:
        priority = Priority.MEDIUM.value
        confidence = 0.75
    else:
        priority = Priority.LOW.value
        confidence = 0.60

    explanation = _build_explanation_from_signals(
        priority=priority,
        confidence=confidence,
        text=text,
        used_model=False,
        urgent_hits=urgent_hits,
        medium_hits=medium_hits,
        casual_hits=casual_hits,
        meta_signals=meta_signals,
    )

    result: Dict[str, Any] = {
        "priority": priority,
        "confidence": confidence,
        "explanation": explanation,
        "raw_text_length": len(text),
    }

    if metadata:
        result["metadata_used"] = list(metadata.keys())

    return result


def format_human_readable_response(
    priority: str,
    confidence: float,
    explanation: str,
    metadata: Optional[Dict[str, Any]] = None,
    text_length: int = 0,
) -> str:
    """
    Format the classification result into a human-readable summary.
    
    Returns a nicely formatted string that's easy to read and understand.
    """
    priority_upper = priority.upper()
    confidence_percent = int(confidence * 100)
    
    # Determine confidence level description
    if confidence >= 0.85:
        confidence_desc = "Very High"
    elif confidence >= 0.70:
        confidence_desc = "High"
    elif confidence >= 0.60:
        confidence_desc = "Moderate"
    else:
        confidence_desc = "Low"
    
    # Build the human-readable summary
    lines = []
    lines.append("=" * 60)
    lines.append("EMAIL PRIORITY CLASSIFICATION RESULT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Priority Level: {priority_upper}")
    lines.append(f"Confidence: {confidence_percent}% ({confidence_desc})")
    lines.append("")
    lines.append("Classification Details:")
    lines.append("-" * 60)
    
    # Extract key information from explanation
    explanation_parts = explanation.split(". ")
    for part in explanation_parts:
        if part.strip() and not part.startswith("[TAG:") and "Confidence=" not in part:
            lines.append(f"  • {part.strip()}")
    
    lines.append("")
    lines.append("Technical Information:")
    lines.append("-" * 60)
    if metadata:
        metadata_keys = list(metadata.keys())
        lines.append(f"  • Metadata fields used: {', '.join(metadata_keys)}")
    lines.append(f"  • Email text length: {text_length} characters")
    
    # Extract tag from explanation
    if "[TAG: ML_MODEL]" in explanation:
        lines.append("  • Classification method: Machine Learning Model")
    elif "[TAG: RULE_BASED]" in explanation:
        lines.append("  • Classification method: Rule-Based Heuristics")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


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
    3. In both cases, produce a meaningful explanation using signals from
       text and metadata.
    """
    if text is None:
        text = ""

    # Analyse text/metadata for explanation signals (works for both ML and rules)
    urgent_hits = _find_keywords(text, URGENT_KEYWORDS)
    medium_hits = _find_keywords(text, MEDIUM_KEYWORDS)
    casual_hits = _find_keywords(text, CASUAL_KEYWORDS)
    meta_signals = _inspect_metadata(metadata)

    # Try ML model first
    _load_model_if_needed()
    used_model = False

    if _MODEL is not None:
        try:
            y_pred = _MODEL.predict([text])[0]
            priority = str(y_pred)

            confidence = 0.8
            if hasattr(_MODEL, "predict_proba"):
                proba = _MODEL.predict_proba([text])[0]
                confidence = float(max(proba))

            used_model = True

            explanation = _build_explanation_from_signals(
                priority=priority,
                confidence=confidence,
                text=text,
                used_model=used_model,
                urgent_hits=urgent_hits,
                medium_hits=medium_hits,
                casual_hits=casual_hits,
                meta_signals=meta_signals,
            )

            result: Dict[str, Any] = {
                "priority": priority,
                "confidence": confidence,
                "explanation": explanation,
                "raw_text_length": len(text),
            }

            if metadata:
                result["metadata_used"] = list(metadata.keys())
            
            # Add human-readable summary
            result["human_readable_summary"] = format_human_readable_response(
                priority=priority,
                confidence=confidence,
                explanation=explanation,
                metadata=metadata,
                text_length=len(text),
            )

            return result

        except Exception:
            logger.exception("ML model failed during classification; falling back to rules.")

    # Fallback: rule-based classification (still with detailed explanation)
    rule_result = _rule_based_classify(text, metadata)
    
    # Add human-readable summary to rule-based result
    rule_result["human_readable_summary"] = format_human_readable_response(
        priority=rule_result["priority"],
        confidence=rule_result["confidence"],
        explanation=rule_result["explanation"],
        metadata=metadata,
        text_length=rule_result["raw_text_length"],
    )
    
    return rule_result
