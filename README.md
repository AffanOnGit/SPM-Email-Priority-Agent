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
