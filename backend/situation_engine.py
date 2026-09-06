import time


COOLDOWN_SECONDS = 60

last_alert_time = 0


def compute_severity(event):

    score = 30

    # ---------------------------------
    # Event type
    # ---------------------------------

    if event["type"] == "collapse":
        score += 20

    elif event["type"] == "seizure":
        score += 35


    # ---------------------------------
    # Immobility
    # ---------------------------------

    motionless = event.get("motionless_sec", 0)

    if motionless >= 3:
        score += 20

    elif motionless >= 2:
        score += 15

    elif motionless >= 1:
        score += 8


    # ---------------------------------
    # Fall / movement evidence
    # ---------------------------------

    fall_velocity = event.get("fall_velocity", 0)

    if fall_velocity > 250:
        score += 15

    elif fall_velocity > 150:
        score += 10


    # ---------------------------------
    # Detector trigger reason
    # ---------------------------------

    trigger = event.get("trigger", "")

    if trigger == "sudden_drop":
        score += 15

    elif trigger == "sustained_horizontal":
        score += 10


    # ---------------------------------
    # Strong horizontal posture
    # ---------------------------------

    torso_angle = event.get("torso_angle", 0)

    if torso_angle >= 60:
        score += 10

    elif torso_angle >= 45:
        score += 5


    # ---------------------------------
    # Night-time context
    # ---------------------------------

    timestamp = event.get("timestamp", "")

    try:

        hour = int(timestamp[11:13])

        if hour >= 22 or hour <= 6:
            score += 10

    except (ValueError, TypeError):

        pass


    return min(int(score), 100)


def get_severity_label(score):

    if score >= 85:
        return "CRITICAL"

    if score >= 65:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def should_alert():

    global last_alert_time

    current_time = time.time()

    if current_time - last_alert_time < COOLDOWN_SECONDS:
        return False

    last_alert_time = current_time

    return True


def process_event(event):

    severity = compute_severity(event)

    label = get_severity_label(severity)

    alert_allowed = should_alert()

    return {
        "severity": severity,
        "label": label,
        "alert": alert_allowed
    }