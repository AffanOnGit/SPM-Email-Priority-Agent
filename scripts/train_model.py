"""
CLI script to train the Email Priority Agent's ML model.

Usage (from project root):
    python scripts/train_model.py
or:
    python -m scripts.train_model
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so "email_agent" can be imported
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from email_agent.learning.model_training import train_and_evaluate
from email_agent.utils.logging_utils import get_logger

logger = get_logger(__name__)


def main() -> None:
    """
    Train the model on the synthetic dataset and print accuracy.
    """
    logger.info("Starting training for Email Priority Agent model...")
    model, accuracy = train_and_evaluate(csv_filename="synthetic_emails.csv")
    logger.info("Training complete. Test accuracy: %.4f", accuracy)

    # Also print to stdout for convenience
    print(f"[Email Priority Agent] Training complete. Test accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    main()
