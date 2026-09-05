import os
import sys
import time
import cv2
import numpy as np

# Import movement from the same folder
try:
    from . import movement
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    import movement

# Constants
ANGLE_THRESHOLD = 45
GAP_THRESHOLD = 0.25
MOTION_THRESHOLD = 0.005
STILLNESS_SECONDS = 3
FPS = 25
ANGLE_JUMP = 15
SUSTAINED_FRAMES = 30

# Module level state variables
state = "NORMAL"
prev_points = None
still_frames = 0
prev_angle = 0.0
fired = False
horizontal_frames = 0
trigger_reason = None


# Updates the fall detection state machine with new landmarks and frame, returning an event if triggered and current status.
def update(landmarks, frame):
    global state, prev_points, still_frames, prev_angle, fired, horizontal_frames, trigger_reason

    if landmarks is None:
        return None, {"state": state, "countdown": None}

    angle = movement.torso_angle(landmarks)
    gap = movement.head_ankle_gap(landmarks)
    motion, prev_points = movement.motion_energy(landmarks, prev_points)

    if angle > ANGLE_THRESHOLD and gap < GAP_THRESHOLD:
        horizontal_frames += 1
    else:
        horizontal_frames = 0

    event = None

    if state == "NORMAL":
        if angle > ANGLE_THRESHOLD and gap < GAP_THRESHOLD and (angle - prev_angle) > ANGLE_JUMP:
            state = "FALL_SUSPECTED"
            still_frames = 0
            trigger_reason = "sudden_drop"
        elif horizontal_frames >= SUSTAINED_FRAMES:
            state = "FALL_SUSPECTED"
            still_frames = 0
            trigger_reason = "sustained_horizontal"
    elif state == "FALL_SUSPECTED":
        if angle < ANGLE_THRESHOLD:
            state = "NORMAL"
            still_frames = 0
            fired = False
        else:
            if motion < MOTION_THRESHOLD:
                still_frames += 1
            else:
                still_frames = 0

            if (still_frames / FPS) >= STILLNESS_SECONDS and not fired:
                state = "EMERGENCY"
                fired = True
                event = {
                    "type": "collapse",
                    "confidence": 0.9,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "motionless_sec": still_frames / FPS,
                    "torso_angle": angle,
                    "motion_energy": motion,
                    "fall_velocity": abs(angle - prev_angle) * FPS,
                    "snapshot_frame": frame,
                    "trigger": trigger_reason,
                }

    prev_angle = angle

    countdown = None
    if state == "FALL_SUSPECTED":
        countdown = max(0.0, STILLNESS_SECONDS - (still_frames / FPS))

    status = {
        "state": state,
        "countdown": countdown,
    }

    return event, status


# Resets all state variables back to their starting values.
def reset():
    global state, prev_points, still_frames, prev_angle, fired, horizontal_frames, trigger_reason
    state = "NORMAL"
    prev_points = None
    still_frames = 0
    prev_angle = 0.0
    fired = False
    horizontal_frames = 0
    trigger_reason = None


if __name__ == "__main__":
    import sys

    # Import camera and pose from the same folder
    try:
        from . import camera, pose
    except ImportError:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        import camera
        import pose

    if len(sys.argv) > 1:
        source = f"videos/{sys.argv[1]}.mp4"
    else:
        source = 0

    cap = camera.open_source(source)
    if cap is None:
        print(f"ERROR: could not open {source}")
        sys.exit(1)

    cv2.namedWindow("VisionSOS - Fall Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("VisionSOS - Fall Detection", 640, 480)

    frame_count = 0

    while True:
        frame = camera.read_frame(cap)
        if frame is None:
            break

        frame_count += 1
        landmarks = pose.get_landmarks(frame)
        event, status = update(landmarks, frame)

        if status["state"] == "FALL_SUSPECTED" and status["countdown"] is not None:
            print(f"frame {frame_count} | {status['state']} | countdown {status['countdown']:.1f}s")
        else:
            print(f"frame {frame_count} | {status['state']} | angle {prev_angle:.1f}")

        if event is not None:
            print("\n" + "=" * 40)
            print("*** EMERGENCY - COLLAPSE ***")
            print(f"Motionless seconds: {event['motionless_sec']:.1f}")
            print(f"Torso angle:        {event['torso_angle']:.1f}")
            print(f"Timestamp:          {event['timestamp']}")
            print("=" * 40 + "\n")

        frame = pose.draw(frame, landmarks)

        color_map = {
            "NORMAL": (0, 255, 0),           # Green
            "FALL_SUSPECTED": (0, 255, 255), # Yellow
            "EMERGENCY": (0, 0, 255),        # Red
        }
        color = color_map.get(status["state"], (255, 255, 255))
        state_text = status["state"]
        if status["countdown"] is not None:
            state_text += f" ({status['countdown']:.1f}s)"

        h, w = frame.shape[:2]
        if w > 640:
            new_height = int(h * (640 / w))
            frame = cv2.resize(frame, (640, new_height))

        cv2.putText(
            frame,
            state_text,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )

        cv2.imshow("VisionSOS - Fall Detection", frame)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    camera.close(cap)
