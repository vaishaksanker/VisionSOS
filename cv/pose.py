import cv2
import mediapipe as mp

# Initialize MediaPipe Pose and drawing utilities once at module level
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils


# Converts the frame from BGR to RGB and returns detected pose landmarks, or None if not found.
def get_landmarks(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    if not results.pose_landmarks:
        return None
    return results.pose_landmarks


# Draws skeleton landmarks and connections on the frame if landmarks exist, otherwise returns the frame unchanged.
def draw(frame, landmarks):
    if landmarks is None:
        return frame
    mp_draw.draw_landmarks(frame, landmarks, mp_pose.POSE_CONNECTIONS)
    return frame


if __name__ == "__main__":
    import os
    import sys

    # Import camera from the same folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    import camera

    if len(sys.argv) > 1:
        source = f"videos/{sys.argv[1]}.mp4"
    else:
        source = 0

    cap = camera.open_source(source)
    cv2.namedWindow("VisionSOS - Pose", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("VisionSOS - Pose", 640, 480)
    frame_count = 0

    while True:
        frame = camera.read_frame(cap)
        if frame is None:
            break

        frame_count += 1
        landmarks = get_landmarks(frame)
        frame = draw(frame, landmarks)

        h, w = frame.shape[:2]
        if w > 640:
            new_height = int(h * (640 / w))
            frame = cv2.resize(frame, (640, new_height))

        cv2.imshow("VisionSOS - Pose", frame)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

        if frame_count % 30 == 0:
            if landmarks is not None:
                print(f"frame {frame_count} | landmarks: FOUND")
            else:
                print(f"frame {frame_count} | landmarks: NONE")

    camera.close(cap)
