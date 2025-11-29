from email_agent.priority_logic import classify_email


def test_classify_email_high_priority():
    text = "Urgent: please submit your report ASAP. The deadline is today."
    result = classify_email(text=text, metadata=None, context=None)

    assert result["priority"] == "high"
    assert result["confidence"] >= 0.8
    assert "urgent" in result["explanation"].lower() or "keyword" in result["explanation"].lower()


def test_classify_email_medium_priority():
    text = "Important: please review the timetable soon."
    result = classify_email(text=text, metadata=None, context=None)

    assert result["priority"] in {"medium", "high"}  # medium by rules, but allow high if model changes
    assert result["confidence"] >= 0.6


def test_classify_email_low_priority():
    text = "Hey, just sharing some memes from yesterday. Check when free."
    result = classify_email(text=text, metadata=None, context=None)

    assert result["priority"] in {"low", "medium"}  # low by default; allow medium if model changes
    assert result["confidence"] >= 0.5
