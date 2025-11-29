# Load synthetic_emails.csv, split train/test
from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import DATA_DIR
from .utils.logging_utils import get_logger

logger = get_logger(__name__)


def load_email_dataset(filename: str = "synthetic_emails.csv") -> pd.DataFrame:
    """
    Load the synthetic email dataset from the data/ folder.

    Expected CSV columns (you can adjust as needed):
    - text      : email text (subject + body)
    - priority  : label ("high" / "medium" / "low")

    Returns:
        pandas.DataFrame with at least 'text' and 'priority' columns.
    """
    path: Path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at: {path}")

    logger.info("Loading email dataset from %s", path)
    df = pd.read_csv(path)
    return df


def train_test_split(
    df: pd.DataFrame, test_ratio: float = 0.2, random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Simple train/test split helper.
    """
    df_shuffled = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    test_size = int(len(df_shuffled) * test_ratio)
    test_df = df_shuffled.iloc[:test_size]
    train_df = df_shuffled.iloc[test_size:]
    logger.info(
        "Split dataset into %d train and %d test examples",
        len(train_df),
        len(test_df),
    )
    return train_df, test_df
