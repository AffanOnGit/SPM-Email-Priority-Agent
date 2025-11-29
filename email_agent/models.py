from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Email:
    """
    Simple internal representation of an email-like item.

    You can extend this later with additional fields if needed.
    """
    text: str
    sender: Optional[str] = None
    subject: Optional[str] = None
    received_at: Optional[str] = None
