import mediapipe as mp
import numpy as np

PoseLandmark = mp.solutions.pose.PoseLandmark


# Extracts the normalized [x, y] coordinates of a given landmark name or enum.
def get_point(landmarks, name):
    if isinstance(name, str):
        idx = PoseLandmark[name].value
    elif hasattr(name, "value"):
        idx = name.value
    else:
        idx = int(name)
    landmark = landmarks.landmark[idx]
    return np.array([landmark.x, landmark.y], dtype=float)


# Computes the torso angle in degrees away from vertical (0=standing, 90=flat).
def torso_angle(landmarks):
    left_shoulder = get_point(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_point(landmarks, PoseLandmark.RIGHT_SHOULDER)
    shoulder_mid = (left_shoulder + right_shoulder) / 2.0

    left_hip = get_point(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = get_point(landmarks, PoseLandmark.RIGHT_HIP)
    hip_mid = (left_hip + right_hip) / 2.0

    dx = abs(shoulder_mid[0] - hip_mid[0])
    dy = abs(shoulder_mid[1] - hip_mid[1])
    angle = np.degrees(np.arctan2(dx, dy))
    return float(abs(angle))


# Computes the absolute vertical distance between the nose and the ankle midpoint.
def head_ankle_gap(landmarks):
    nose = get_point(landmarks, PoseLandmark.NOSE)
    left_ankle = get_point(landmarks, PoseLandmark.LEFT_ANKLE)
    right_ankle = get_point(landmarks, PoseLandmark.RIGHT_ANKLE)
    ankle_avg_y = (left_ankle[1] + right_ankle[1]) / 2.0
    return float(abs(nose[1] - ankle_avg_y))


# Computes the mean Euclidean displacement of all 33 landmarks across frames.
def motion_energy(landmarks, prev_points):
    current_points = np.array(
        [[lm.x, lm.y] for lm in landmarks.landmark], dtype=float
    )
    if prev_points is None:
        return (0.0, current_points)
    distances = np.linalg.norm(current_points - prev_points, axis=1)
    return (float(np.mean(distances)), current_points)


if __name__ == "__main__":
    import os
    import sys
    import cv2

    # Import camera and pose from the same folder
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
    prev_points = None
    frame_count = 0

    while True:
        frame = camera.read_frame(cap)
        if frame is None:
            break

        frame_count += 1
        landmarks = pose.get_landmarks(frame)
        if landmarks is None:
            print(f"frame {frame_count} | NO LANDMARKS")
            continue

        angle = torso_angle(landmarks)
        gap = head_ankle_gap(landmarks)
        motion, prev_points = motion_energy(landmarks, prev_points)

        print(
            f"frame {frame_count} | angle: {angle:5.1f} | gap: {gap:.3f} | motion: {motion:.4f}"
        )

        frame = pose.draw(frame, landmarks)
        cv2.imshow("VisionSOS - Movement", frame)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    camera.close(cap)
