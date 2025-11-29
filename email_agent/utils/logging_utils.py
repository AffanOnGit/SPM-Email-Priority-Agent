import logging
import sys
from typing import Optional

_LOGGER_CONFIGURED = False


def _configure_root_logger() -> None:
    """
    Configure the root logger once with a standard format.
    """
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    _LOGGER_CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a logger with a standard format.

    Usage:
        logger = get_logger(__name__)
        logger.info("Some message")
    """
    _configure_root_logger()
    return logging.getLogger(name)
