from typing import Optional, Dict, Any
from pydantic import BaseModel


class InputPayload(BaseModel):
    """
    Represents the 'input' field from the Supervisor's handshake.

    Example:
    {
      "text": "some email-like text",
      "metadata": { "sender": "...", "subject": "...", ... }
    }
    """
    text: str
    metadata: Optional[Dict[str, Any]] = None


class ContextPayload(BaseModel):
    """
    Represents the optional 'context' field from the handshake.

    Example:
    {
      "user_id": "user-123",
      "conversation_id": "conv-xyz",
      "timestamp": "2025-11-29T08:10:00Z",
      "extras": { ... }
    }
    """
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    timestamp: Optional[str] = None
    extras: Optional[Dict[str, Any]] = None


class AgentRequest(BaseModel):
    """
    Python representation of the handshake JSON the Supervisor sends.

    Fields should match the integration doc:
    - request_id: unique ID for this call (string, may be None for testing)
    - agent_name: target agent's name (should be "email_priority_agent")
    - intent: e.g. "email.priority.classify"
    - input: nested InputPayload with text + metadata
    - context: optional ContextPayload
    """
    request_id: Optional[str] = None
    agent_name: Optional[str] = None
    intent: str
    input: InputPayload
    context: Optional[ContextPayload] = None


class AgentResponse(BaseModel):
    """
    Python representation of the JSON we return to the Supervisor.

    - request_id: echo back the original ID (if we have one)
    - agent_name: this agent's name ("email_priority_agent")
    - status: "success" or "error"
    - output: result payload on success (dict)
    - error:  error payload on failure (dict with "type" and "message")
    """
    request_id: Optional[str]
    agent_name: str
    status: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
