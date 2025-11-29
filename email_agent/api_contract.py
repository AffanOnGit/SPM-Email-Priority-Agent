"""
Python-side documentation of the Email Priority Agent's JSON API contract.

You don't have to import this anywhere; it's mainly for clarity and for
generating content for docs/api_contract.md.
"""

HANDLER_REQUEST_EXAMPLE = {
    "request_id": "uuid-123",
    "agent_name": "email_priority_agent",
    "intent": "email.priority.classify",
    "input": {
        "text": "Urgent: please submit your project report by tonight.",
        "metadata": {
            "sender": "boss@example.com",
            "subject": "Urgent project deadline",
            "received_at": "2025-11-29T08:10:00Z",
        },
    },
    "context": {
        "user_id": "demo-user-1",
        "conversation_id": "conv-001",
        "timestamp": "2025-11-29T08:10:00Z",
    },
}

HANDLER_RESPONSE_SUCCESS_EXAMPLE = {
    "request_id": "uuid-123",
    "agent_name": "email_priority_agent",
    "status": "success",
    "output": {
        "priority": "high",
        "confidence": 0.92,
        "explanation": "Detected urgent keywords in the email text.",
    },
    "error": None,
}
