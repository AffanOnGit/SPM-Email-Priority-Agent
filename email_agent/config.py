from pathlib import Path

# Name must match the name you put in Supervisor's registry.py
AGENT_NAME = "email_priority_agent"

# Optional: default intents for docs / logging
DEFAULT_INTENTS = ["email.priority.classify"]

# Base directory: project root (SPM-Email-Priority-Agent)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data/model paths
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = DATA_DIR / "models"
MODEL_PATH = MODEL_DIR / "email_priority_model.pkl"

# Long-Term Memory (LTM) storage
LTM_DIR = BASE_DIR / "ltm"
LTM_INDEX_PATH = LTM_DIR / "ltm_index.json"
LTM_RECORDS_DIR = LTM_DIR / "records"

# You can add other config flags here later (thresholds, etc.)
