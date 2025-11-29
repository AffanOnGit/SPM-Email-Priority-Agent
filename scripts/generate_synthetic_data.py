"""
Script to generate a simple synthetic email dataset for the Email Priority Agent.

It creates data/synthetic_emails.csv with two columns:
- text     : email-like text
- priority : label ("high" / "medium" / "low")

Usage (from project root):
    python scripts/generate_synthetic_data.py
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so "email_agent" can be imported
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from pathlib import Path
import random

import pandas as pd

from email_agent.config import DATA_DIR
from email_agent.utils.logging_utils import get_logger

logger = get_logger(__name__)


HIGH_TEMPLATES = [
    "Urgent: please submit the {item} by tonight.",
    "ASAP: we need your response regarding {item}.",
    "Immediate attention required: {item} deadline is today.",
    "Critical update: {item} must be fixed within the next 2 hours.",
]

MEDIUM_TEMPLATES = [
    "Important: please review the {item} soon.",
    "Reminder: don't forget to check the {item} this week.",
    "Please look over the {item} when you have time.",
    "Follow-up: we would appreciate your feedback on the {item}.",
]

LOW_TEMPLATES = [
    "Hey, just sharing some memes about {item}.",
    "FYI: there is a new newsletter about {item}.",
    "Random thought: {item} looks interesting.",
    "No rush: check out this article on {item} whenever you're free.",
]

ITEMS = [
    "project report",
    "team meeting",
    "assignment submission",
    "system update",
    "course feedback",
    "lab evaluation",
    "exam schedule",
    "new policy",
]


def generate_examples(n_per_class: int = 100) -> pd.DataFrame:
    """
    Generate a simple synthetic dataset with roughly balanced classes.
    """
    rows = []

    # High priority
    for _ in range(n_per_class):
        template = random.choice(HIGH_TEMPLATES)
        item = random.choice(ITEMS)
        text = template.format(item=item)
        rows.append({"text": text, "priority": "high"})

    # Medium priority
    for _ in range(n_per_class):
        template = random.choice(MEDIUM_TEMPLATES)
        item = random.choice(ITEMS)
        text = template.format(item=item)
        rows.append({"text": text, "priority": "medium"})

    # Low priority
    for _ in range(n_per_class):
        template = random.choice(LOW_TEMPLATES)
        item = random.choice(ITEMS)
        text = template.format(item=item)
        rows.append({"text": text, "priority": "low"})

    random.shuffle(rows)
    df = pd.DataFrame(rows)
    return df


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path: Path = DATA_DIR / "synthetic_emails.csv"

    logger.info("Generating synthetic email dataset...")
    df = generate_examples(n_per_class=200)  # total 600 rows
    df.to_csv(output_path, index=False)
    logger.info("Saved synthetic dataset to %s", output_path)
    print(f"Synthetic dataset saved to: {output_path}")


if __name__ == "__main__":
    main()
