# Email Priority Agent

This repository implements the Email Priority Agent — a small worker
service that classifies email-like text into priority levels (`high`,
`medium`, `low`). The agent exposes a simple HTTP handshake used by a
Supervisor agent and includes a lightweight long-term memory (LTM)
cache and an optional scikit-learn model for improved classification.

**Quick overview:** the Flask app (`app.py`) delegates business logic
to the `email_agent` package. Model training and dataset generation
live under `scripts/` and `email_agent/learning/`.

---

**Why this repo exists**

- Provide a reproducible, testable email priority classifier for a
  multi-agent supervisor setup.
- Demonstrate a minimal ML workflow (train → persist → serve).

---

**Project Layout (important files)**

- `app.py`: Flask application with `/health` and `/handle` endpoints.
- `email_agent/`: core package (config, handshake schemas, priority
  logic, LTM store, model training helpers).
- `data/`: contains `synthetic_emails.csv` and `data/models/` for
  persisted model artifacts.
- `ltm/`: runtime LTM index and records (used by `email_agent.ltm_store`).
- `scripts/`: helper scripts: `train_model.py`, `generate_synthetic_data.py`.
- `tests/`: pytest test-suite for unit and integration tests.
- `requirements.txt`: Python dependencies.

---

**Supported features**

- Rule-based classification with keyword signals.
- Optional scikit-learn model pipeline (TF-IDF + LogisticRegression).
- Long-Term Memory (LTM) for caching repeated inputs.
- Unit tests with `pytest`.

**Note:** The repository intentionally keeps ML/model code separate
from the HTTP handshake and service layer to keep the agent modular.

---

**Getting Started (local development)**

Prerequisites:

- Python 3.11 (recommended)
- `pip` available

1) Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3) Run the Flask app (development mode):

```powershell
# From project root
python app.py
```

The app will start on `http://0.0.0.0:5000` by default (dev server).

---

**Run with Gunicorn (production-style)**

The included `Dockerfile` expects the service to run with `gunicorn`.
Locally you can run the same command used in the container (make sure
`gunicorn` is installed):

```powershell
# Bind to port 8000 (example)
gunicorn -b 0.0.0.0:8000 app:app
```

Or build and run the Docker image:

```powershell
# From repo root
docker build -t email-priority-agent .
# Expose and run (map 8000 container port to 8000 host port)
docker run -p 8000:8000 --rm email-priority-agent
```

> Note: the `Dockerfile` exposes port `8000` and runs `gunicorn` by
> default. Adjust the port mapping as needed for your environment.

---

**API: Handshake contract (summary)**

- `GET /health` — healthcheck used by the Supervisor. Returns JSON with
  `status`, `agent`, and small `message`.
- `POST /handle` — main handler. Expects a JSON payload that matches
  the `email_agent.handshake_schemas.AgentRequest` model. On success
  returns an `AgentResponse` with `status: success` and an `output`
  payload containing `priority`, `confidence`, and `explanation`.

See `email_agent/api_contract.py` and `email_agent/handshake_schemas.py`
for exact examples and types.

---

**Training the model (optional)**

If you want to train the scikit-learn model locally using the provided
synthetic dataset:

```powershell
# (activate virtualenv first)
python -m scripts.train_model
# or
python scripts/train_model.py
```

This will build a TF-IDF + LogisticRegression pipeline and persist the
model to `data/models/email_priority_model.pkl` (see
`email_agent/learning/model_store.py`).

If you need more synthetic data, run:

```powershell
python -m scripts.generate_synthetic_data
# or
python scripts/generate_synthetic_data.py
```

---

**Running tests**

Run the test suite with `pytest` from the project root:

```powershell
# (activate virtualenv)
pytest -q
```

Tests exercise the LTM store, priority logic rules, and HTTP
handshake endpoints (via Flask test client).

---

**Long-Term Memory (LTM)**

- Runtime LTM files live under the `ltm/` directory. The index is stored
  at `ltm/ltm_index.json` and record files are under `ltm/records/`.
- The `.gitignore` intentionally excludes `ltm/records/` and
  `ltm/ltm_index.json` to avoid committing runtime data. If you want to
  keep specific LTM entries committed, remove them from `.gitignore`.

---

**Development tips & changelog**

- The main HTTP entrypoint is `app.py`. Keep business logic inside
  `email_agent/` to make testing and reuse easier.
- Use `email_agent.utils.logging_utils.get_logger` to obtain a
  standardized logger.

---

**Contributing**

If you plan to contribute, please:

- Open an issue describing the feature or bug.
- Add tests under `tests/` for any logic you change.

---

If you'd like, I can also:

- Add a short `Makefile` or PowerShell helper script for common tasks
  (run, test, train).
- Add example `curl` requests for the `/handle` endpoint.

---

*Last updated: 2025-11-30*
# Email Priority Agent

This repository implements the **Email Priority Worker Agent** for the
_Fundamentals of Software Project Management_ semester project.

The agent is exposed as a standalone **HTTP service** that the
**Supervisor Agent** calls via a standardized JSON handshake.

---

## 1. Features (Conceptual)

- Accepts a text input that represents an email (subject/body-like text).
- Classifies the email into priority levels: **high**, **medium**, or **low**.
- Optionally returns additional information such as:
  - Confidence score
  - Short explanation of the decision
- Uses:
  - A trained **scikit-learn** model for priority classification.
  - A simple **Long-Term Memory (LTM)** layer to cache repeated tasks.
- Provides:
  - `/handle` endpoint: main classification handler.
  - `/health` endpoint: simple healthcheck for the Supervisor.

---

## 2. Project Structure (High-Level)

```text
email-priority-agent/
  ├─ app.py                  # Flask app: /handle and /health
  ├─ email_agent/            # Core logic (ML, LTM, schemas, utils)
  ├─ data/                   # Synthetic dataset + trained model
  ├─ ltm/                    # Long-term memory storage
  ├─ tests/                  # Unit / integration tests
  ├─ scripts/                # Helper scripts (train model, generate data)
  ├─ docs/                   # Design, API contract, memory strategy
  ├─ requirements.txt
