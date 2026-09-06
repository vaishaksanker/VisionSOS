import os
import cv2

from backend.situation_engine import process_event
from alerts.twilio_sms import send_sms
from database.database import save_event


EVENTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "events"
)

os.makedirs(EVENTS_DIR, exist_ok=True)


def save_snapshot(frame, event_type):
    """Save the emergency frame and return its file path."""

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{event_type}_{timestamp}.jpg"
    filepath = os.path.join(EVENTS_DIR, filename)

    cv2.imwrite(filepath, frame)

    return filepath


def handle_event(event):
    """
    Process a CV event and handle the emergency response.
    """

    print("\n=== EVENT HANDLER ===")

    # 1. Situation Engine
    result = process_event(event)

    severity = result["severity"]
    label = result["label"]
    alert_allowed = result["alert"]

    print(f"[ENGINE] Severity: {severity}/100")
    print(f"[ENGINE] Label: {label}")
    print(f"[ENGINE] Alert allowed: {alert_allowed}")

    # 2. Save snapshot
    snapshot_path = save_snapshot(
        event["snapshot_frame"],
        event["type"]
    )

    print(f"[SNAPSHOT] Saved: {snapshot_path}")

    # 3. Send predefined Twilio trial SMS
    alert_sent = False

    if alert_allowed:
        alert_sent = send_sms()

        if alert_sent:
            print("[ALERT] SMS sent")
        else:
            print("[ALERT] SMS failed")

    else:
        print("[ALERT] Suppressed because of cooldown")

    # 4. Save event to database
    event_id = save_event(
        event,
        severity,
        label,
        snapshot_path,
        alert_sent
    )

    print(f"[EVENT] Stored as event #{event_id}")

    return {
        "event_id": event_id,
        "severity": severity,
        "label": label,
        "alert_sent": alert_sent,
        "snapshot_path": snapshot_path
    }