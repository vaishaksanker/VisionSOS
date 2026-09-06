import os
import sys
import time
import threading

import cv2

from cv import camera
from cv import pose
from cv import fall_detection

from backend.app import app
from backend.event_handler import handle_event

from backend.system_state import (
    write_status,
    write_event,
    set_system_active
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LIVE_FRAME_PATH = os.path.join(
    BASE_DIR,
    "events",
    "live_frame.jpg"
)

os.makedirs(
    os.path.dirname(LIVE_FRAME_PATH),
    exist_ok=True
)


# ============================================================
# VIDEO SOURCE
# ============================================================

def get_video_source():

    if len(sys.argv) <= 1:
        return 0

    source_arg = sys.argv[1]

    # Example:
    # python main.py fall1.MOV

    # Direct path
    if os.path.isfile(source_arg):
        return source_arg

    # File inside videos/
    videos_path = os.path.join(
        BASE_DIR,
        "videos",
        source_arg
    )

    if os.path.isfile(videos_path):
        return videos_path

    # Try .mp4
    videos_mp4 = os.path.join(
        BASE_DIR,
        "videos",
        source_arg + ".mp4"
    )

    if os.path.isfile(videos_mp4):
        return videos_mp4

    print()
    print(
        f"[ERROR] Video not found: {source_arg}"
    )

    print(
        "[INFO] Put videos inside the videos/ folder."
    )

    sys.exit(1)


# ============================================================
# FLASK SERVER
# ============================================================

def run_flask():

    print()
    print("=" * 50)
    print("VisionSOS Dashboard")
    print("=" * 50)
    print("Open: http://127.0.0.1:5000")
    print("=" * 50)
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )


# ============================================================
# SAVE LIVE FRAME
# ============================================================

def save_live_frame(frame):

    # IMPORTANT:
    # The temporary file must also end in .jpg.
    # Otherwise OpenCV sees ".tmp" and doesn't know
    # which image encoder to use.

    temp_path = os.path.join(
        os.path.dirname(LIVE_FRAME_PATH),
        "live_frame_tmp.jpg"
    )

    success = cv2.imwrite(
        temp_path,
        frame,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            80
        ]
    )

    if success:

        try:

            os.replace(
                temp_path,
                LIVE_FRAME_PATH
            )

        except Exception as e:

            print(
                f"[FRAME] Could not update live frame: {e}"
            )

    else:

        print(
            "[FRAME] Failed to write live frame"
        )


# ============================================================
# COMPUTER VISION
# ============================================================

def run_detection(source):

    print()
    print("=" * 50)
    print("VisionSOS Computer Vision")
    print("=" * 50)
    print(f"Source: {source}")
    print("Press Q to quit")
    print("=" * 50)
    print()

    # Reset detector before starting
    fall_detection.reset()

    cap = camera.open_source(
        source
    )

    if cap is None:

        print(
            f"[ERROR] Could not open source: {source}"
        )

        set_system_active(False)

        return

    frame_count = 0

    try:

        while True:

            # ==================================================
            # READ FRAME
            # ==================================================

            frame = camera.read_frame(
                cap
            )

            if frame is None:

                print()
                print(
                    "[CV] Video finished."
                )

                break

            frame_count += 1


            # ==================================================
            # POSE DETECTION
            # ==================================================

            landmarks = pose.get_landmarks(
                frame
            )


            # ==================================================
            # FALL DETECTION
            # ==================================================

            event, status = fall_detection.update(
                landmarks,
                frame
            )

            current_state = status["state"]

            countdown = status["countdown"]


            # ==================================================
            # UPDATE DASHBOARD STATE
            # ==================================================

            write_status(
                current_state,
                countdown
            )


            # ==================================================
            # DRAW MEDIAPIPE POSE
            # ==================================================

            display_frame = pose.draw(
                frame,
                landmarks
            )


            # ==================================================
            # STATE COLORS
            # ==================================================

            color_map = {

                "NORMAL":
                    (0, 255, 0),

                "FALL_SUSPECTED":
                    (0, 255, 255),

                "EMERGENCY":
                    (0, 0, 255)
            }

            color = color_map.get(
                current_state,
                (255, 255, 255)
            )


            # ==================================================
            # STATE TEXT
            # ==================================================

            status_text = current_state

            if countdown is not None:

                status_text += (
                    f"  {countdown:.1f}s"
                )


            cv2.putText(
                display_frame,
                status_text,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2,
                cv2.LINE_AA
            )


            # ==================================================
            # SYSTEM LABEL
            # ==================================================

            cv2.putText(
                display_frame,
                "VisionSOS AI Monitoring",
                (30, 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )


            # ==================================================
            # SAVE FRAME FOR DASHBOARD
            # ==================================================

            save_live_frame(
                display_frame
            )


            # ==================================================
            # EMERGENCY EVENT
            # ==================================================

            if event is not None:

                print()
                print("=" * 50)
                print(
                    "       VISION SOS EMERGENCY"
                )
                print("=" * 50)

                print(
                    f"Event: "
                    f"{event['type']}"
                )

                print(
                    f"Confidence: "
                    f"{event['confidence']}"
                )

                print(
                    f"Motionless: "
                    f"{event['motionless_sec']:.1f}s"
                )

                print(
                    f"Torso angle: "
                    f"{event['torso_angle']:.1f}°"
                )

                print(
                    f"Trigger: "
                    f"{event.get('trigger', 'unknown')}"
                )

                print("=" * 50)


                # ==================================================
                # BACKEND EVENT HANDLER
                # ==================================================

                result = handle_event(
                    event
                )


                # ==================================================
                # SEND RESULT TO DASHBOARD
                # ==================================================

                write_event(
                    result
                )


                print()
                print(
                    "[RESPONSE COMPLETE]"
                )

                print(
                    f"Event ID: "
                    f"{result['event_id']}"
                )

                print(
                    f"Severity: "
                    f"{result['severity']}/100"
                )

                print(
                    f"Level: "
                    f"{result['label']}"
                )

                print(
                    f"SMS sent: "
                    f"{result['alert_sent']}"
                )

                print(
                    f"Snapshot: "
                    f"{result['snapshot_path']}"
                )

                print("=" * 50)
                print()


            # ==================================================
            # TERMINAL STATUS
            # ==================================================

            if current_state == "FALL_SUSPECTED":

                print(
                    f"[CV] FALL SUSPECTED | "
                    f"Countdown: "
                    f"{countdown:.1f}s"
                )

            elif current_state == "EMERGENCY":

                print(
                    "[CV] 🚨 EMERGENCY"
                )


            # ==================================================
            # LOCAL OPENCV WINDOW
            # ==================================================

            cv2.imshow(
                "VisionSOS - Computer Vision",
                display_frame
            )


            # ==================================================
            # QUIT
            # ==================================================

            key = cv2.waitKey(30) & 0xFF

            if key == ord("q"):

                break


    finally:

        camera.close(
            cap
        )

        set_system_active(
            False
        )

        print()
        print(
            "VisionSOS stopped."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    # Determine video/webcam
    source = get_video_source()


    # Start Flask dashboard
    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()


    # Give Flask a moment to start
    time.sleep(1)


    # Mark system active
    set_system_active(
        True
    )


    # Start computer vision
    run_detection(
        source
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()