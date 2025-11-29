# Accuracy, confusion matrix, etc.
from typing import List, Any

from sklearn.metrics import accuracy_score, classification_report

from .logging_utils import get_logger

logger = get_logger(__name__)


def evaluate_classifier(model: Any, X_test: List[str], y_test: List[str]) -> float:
    """
    Compute accuracy and log a basic classification report.

    Returns:
        accuracy (float between 0 and 1)
    """
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info("Classification report:\n%s", classification_report(y_test, y_pred))
    return acc
