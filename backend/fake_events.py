# backend/fake_events.py
import random
import numpy as np
from datetime import datetime


def fake_event():
    """
    Generate a fake emergency event for testing the backend.

    This event uses the same format that the CV module
    will eventually send to the backend.
    """

    event_type = random.choice(["collapse", "seizure"])

    event = {
        "type": event_type,
        "confidence": 0.87,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "motionless_sec": 8.2,
        "torso_angle": 78.4,
        "motion_energy": 0.008,
        "fall_velocity": 312.0,

        # Temporary black image used as a fake camera frame.
        # Later this will come from Sidharth's CV module.
        "snapshot_frame": np.zeros(
            (480, 640, 3),
            dtype=np.uint8
        )
    }

    return event


if __name__ == "__main__":
    event = fake_event()

    print("=== FAKE EMERGENCY EVENT ===")
    print("Type:", event["type"])
    print("Confidence:", event["confidence"])
    print("Motionless:", event["motionless_sec"], "seconds")
    print("Torso angle:", event["torso_angle"])
    print("Motion energy:", event["motion_energy"])
    print("Fall velocity:", event["fall_velocity"])
    print("Snapshot shape:", event["snapshot_frame"].shape)