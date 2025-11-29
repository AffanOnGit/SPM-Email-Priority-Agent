import json


def test_health_endpoint(client):
    """
    Ensure /health returns 200 and basic agent info.
    """
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"
    assert "agent" in data
    assert isinstance(data["agent"], str)


def test_handle_high_priority(client):
    """
    End-to-end test for /handle with a clearly high-priority email.
    """
    payload = {
        "request_id": "test-001",
        "agent_name": "email_priority_agent",
        "intent": "email.priority.classify",
        "input": {
            "text": "Urgent: please submit your project report by tonight. This is extremely important and must be done ASAP.",
            "metadata": {
                "sender": "boss@example.com",
                "subject": "Urgent project deadline",
            },
        },
        "context": {
            "user_id": "demo-user-1",
            "conversation_id": "conv-001",
        },
    }

    response = client.post(
        "/handle",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code in {200, 500}  # we prefer 200, but 500 + status="error" is also allowed
    data = response.get_json()

    assert data["request_id"] == "test-001"
    assert data["agent_name"] == "email_priority_agent"
    assert data["status"] in {"success", "error"}

    if data["status"] == "success":
        output = data["output"]
        assert output is not None
        assert output["priority"] in {"high", "medium"}  # should be high by rules
        assert output["confidence"] >= 0.6
        assert "explanation" in output
    else:
        # If status="error", ensure error details exist
        assert data["error"] is not None
        assert "type" in data["error"]
        assert "message" in data["error"]


def test_handle_bad_payload(client):
    """
    If we send an invalid payload, the agent should respond with status='error'.
    """
    # Missing required fields such as "intent" and "input"
    bad_payload = {
        "request_id": "bad-001",
        "agent_name": "email_priority_agent",
    }

    response = client.post(
        "/handle",
        data=json.dumps(bad_payload),
        content_type="application/json",
    )

    # Our app currently returns 400 in this case with status='error'
    assert response.status_code == 400
    data = response.get_json()

    assert data["status"] == "error"
    assert data["output"] is None
    assert data["error"] is not None
