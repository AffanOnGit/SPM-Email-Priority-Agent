"""
Main Flask application for the Email Priority Agent.

Exposes:
- GET  /health  : healthcheck endpoint used by the Supervisor
- POST /handle  : main handler endpoint that follows the agreed handshake contract

This file should NOT contain core ML / business logic.
It should delegate to the email_agent package (priority_logic, ltm_store, etc.).
"""

from flask import Flask, jsonify, request

# These modules will live under email_agent/ (we'll define them later).
from email_agent.config import AGENT_NAME
from email_agent.handshake_schemas import AgentRequest, AgentResponse
from email_agent.priority_logic import classify_email
from email_agent.ltm_store import lookup, store
from email_agent.utils.logging_utils import get_logger

app = Flask(__name__)
logger = get_logger(__name__)


@app.route("/health", methods=["GET"])
def health() -> tuple:
    """
    Simple healthcheck endpoint.

    The supervisor will call this to verify that the agent is alive.
    Keep the response small and stable.
    """
    response_body = {
        "status": "ok",
        "agent": AGENT_NAME,
        "message": "Email Priority Agent is healthy.",
    }
    return jsonify(response_body), 200


@app.route("/handle", methods=["POST"])
def handle() -> tuple:
    """
    Main handler endpoint.

    Expected JSON body from Supervisor (handshake):
    {
      "request_id": "...",
      "agent_name": "email_priority_agent",
      "intent": "email.priority.classify",
      "input": {
        "text": "some email-like text",
        "metadata": {...}   # optional
      },
      "context": {
        ...                 # optional contextual information
      }
    }

    Response JSON:
    {
      "request_id": "...",   # echo
      "agent_name": "email_priority_agent",
      "status": "success" | "error",
      "output": { ... } | null,
      "error":  { "type": "...", "message": "..." } | null
    }
    """
    try:
        raw_json = request.get_json(force=True, silent=False)
        logger.info("Received /handle request: %s", raw_json)

        # Parse & validate handshake into internal model
        agent_request = AgentRequest.model_validate(raw_json)

    except Exception as exc:
        # Any parsing/validation / unexpected error before we have a request_id
        logger.exception("Failed to parse AgentRequest")
        # We may not have a request_id; send a generic response.
        error_response = AgentResponse(
            request_id=None,
            agent_name=AGENT_NAME,
            status="error",
            output=None,
            error={
                "type": "BadRequest",
                "message": f"Invalid request payload: {exc}",
            },
        )
        return jsonify(error_response.model_dump()), 400

    # At this point we have a valid AgentRequest, including request_id.
    try:
        # Build a deterministic task key for LTM (can refine later)
        task_key = f"{agent_request.intent}:{agent_request.input.text}"

        # 1) Try long-term memory first
        cached_result = lookup(task_key)
        if cached_result is not None:
            logger.info("LTM hit for task_key=%s", task_key)
            result_payload = cached_result
            # Ensure cached results also have human_readable_summary (for backward compatibility)
            if "human_readable_summary" not in result_payload:
                from email_agent.priority_logic import format_human_readable_response
                result_payload["human_readable_summary"] = format_human_readable_response(
                    priority=result_payload.get("priority", "unknown"),
                    confidence=result_payload.get("confidence", 0.0),
                    explanation=result_payload.get("explanation", ""),
                    metadata=agent_request.input.metadata,
                    text_length=result_payload.get("raw_text_length", 0),
                )
        else:
            logger.info("LTM miss for task_key=%s; invoking core logic", task_key)

            # 2) Call core classification logic (ML model + rules)
            result_payload = classify_email(
                text=agent_request.input.text,
                metadata=agent_request.input.metadata,
                context=agent_request.context,
            )

            # 3) Store successful result in LTM
            try:
                store(task_key, result_payload)
            except Exception:
                # LTM failures should not break the main flow
                logger.exception("Failed to store result in LTM for task_key=%s", task_key)

        # 4) Build a success response with properly formatted output
        agent_response = AgentResponse(
            request_id=agent_request.request_id,
            agent_name=AGENT_NAME,
            status="success",
            # NEST the result payload under "result"
            output={"result": result_payload},
            error=None,
        )
        
        # Log the human-readable summary for debugging
        if "human_readable_summary" in result_payload:
            logger.info("Classification result:\n%s", result_payload["human_readable_summary"])
        
        return jsonify(agent_response.model_dump()), 200

    except Exception as exc:
        # Any runtime error in business logic should result in a structured error response
        logger.exception("Error while handling request_id=%s", agent_request.request_id)
        error_response = AgentResponse(
            request_id=agent_request.request_id,
            agent_name=AGENT_NAME,
            status="error",
            output=None,
            error={
                "type": type(exc).__name__,
                "message": str(exc),
            },
        )
        # You can choose 500 or 200 with status="error"; using 500 is clearer for infra.
        return jsonify(error_response.model_dump()), 500


if __name__ == "__main__":
    # For local dev; in production you may use gunicorn/uvicorn to serve this app.
    app.run(host="0.0.0.0", port=5000, debug=True)
