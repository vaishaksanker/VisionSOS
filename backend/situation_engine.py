# backend/situation_engine.py
# backend/situation_engine.py

import time


# Prevent the same emergency from triggering alerts repeatedly.
COOLDOWN_SECONDS = 60

last_alert_time = 0


def compute_severity(event):
    """
    Calculate an explainable emergency severity score from 0 to 100.
    """

    score = 40

    # Longer immobility increases severity.
    score += min(event["motionless_sec"] * 2, 25)

    # A fast fall can indicate a more serious collapse.
    if event["fall_velocity"] > 250:
        score += 15

    # Rhythmic movement is treated as an additional risk signal.
    if event["type"] == "seizure":
        score += 10

    # Night-time events receive a small additional priority.
    hour = int(event["timestamp"][11:13])

    if hour >= 22 or hour <= 6:
        score += 10

    return min(int(score), 100)


def get_severity_label(score):
    """
    Convert the numerical risk score into a human-readable level.
    """

    if score >= 85:
        return "CRITICAL"

    if score >= 65:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def should_alert():
    """
    Prevent duplicate alerts during the same emergency.
    """

    global last_alert_time

    current_time = time.time()

    if current_time - last_alert_time < COOLDOWN_SECONDS:
        return False

    last_alert_time = current_time

    return True


def process_event(event):
    """
    Main entry point for the Situation Engine.

    Receives an event from the CV system and returns
    the severity and alert decision.
    """

    severity = compute_severity(event)
    label = get_severity_label(severity)

    alert_allowed = should_alert()

    result = {
        "severity": severity,
        "label": label,
        "alert": alert_allowed
    }

    return result