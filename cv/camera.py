import cv2
import sys


# Opens a video capture source (webcam or video file) and returns the capture object.
def open_source(source=0):
    if source == 0 or source == "webcam":
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print(f"ERROR: could not open {source}")
            return None
        print("Opened: webcam")
    else:
        path = source
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(f"ERROR: could not open {source}")
            return None
        print(f"Opened: {path}")
        print(f"Total frame count: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}")
    return cap


# Reads the next frame from the capture object, returning the frame or None if finished.
def read_frame(cap):
    if cap is None:
        return None
    ret, frame = cap.read()
    if ret:
        return frame
    return None


# Releases the capture object and closes all OpenCV windows.
def close(cap):
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        source = f"videos/{sys.argv[1]}.mp4"
    else:
        source = 0

    cap = open_source(source)
    frame_count = 0

    while True:
        frame = read_frame(cap)
        if frame is None:
            break
        frame_count += 1
        cv2.imshow("VisionSOS", frame)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break
        if frame_count % 30 == 0:
            print(f"frame {frame_count}")

    print(f"Finished. Total frames read: {frame_count}")
    close(cap)
