# Train scikit-learn model (offline script)
from typing import Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

from ..data_loader import load_email_dataset, train_test_split
from ..utils.logging_utils import get_logger
from ..utils.evaluation_utils import evaluate_classifier
from .model_store import save_model

logger = get_logger(__name__)


def build_pipeline() -> Pipeline:
    """
    Build a simple scikit-learn pipeline for text classification.

    - TfidfVectorizer: converts text to numerical features
    - LogisticRegression: classifier

    You can change the model later (e.g., SVM, Naive Bayes, etc.).
    """
    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=500)),
        ]
    )
    return pipeline


def train_and_evaluate(
    csv_filename: str = "synthetic_emails.csv",
) -> Tuple[Pipeline, float]:
    """
    Train the classifier on the synthetic dataset and evaluate accuracy.

    Returns:
        (trained_pipeline, accuracy)
    """
    df = load_email_dataset(csv_filename)
    if "text" not in df.columns or "priority" not in df.columns:
        raise ValueError("Dataset must contain 'text' and 'priority' columns.")

    train_df, test_df = train_test_split(df)

    X_train = train_df["text"].tolist()
    y_train = train_df["priority"].tolist()

    X_test = test_df["text"].tolist()
    y_test = test_df["priority"].tolist()

    pipeline = build_pipeline()
    logger.info("Starting model training on %d examples...", len(X_train))
    pipeline.fit(X_train, y_train)
    logger.info("Training completed.")

    accuracy = evaluate_classifier(pipeline, X_test, y_test)
    logger.info("Model accuracy on test set: %.4f", accuracy)

    # Save the model for use at runtime
    save_model(pipeline)

    return pipeline, accuracy


if __name__ == "__main__":
    # This allows you to run training via:
    # python -m email_agent.learning.model_training
    model, acc = train_and_evaluate()
    print(f"Training complete. Test accuracy: {acc:.4f}")
