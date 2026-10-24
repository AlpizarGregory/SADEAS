import cv2
import time
import os

from threading import Thread
from queue import Queue, Empty

# Capture parameters
VIDEO_WIDHT = 1920
VIDEO_HEIGHT = 1080
TARGET_FPS = 30.0
DEVICE_ID = 0 # /dev/video0

# Videos directory
OUTPUT_DIR = "/home/alpizargregory/sadeas_videos"

def setup():
    print("Starting setup")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # File name based on current timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, "sadeas_capture_{}.avi".format(timestamp))

    # Initialize capture from V4L2
    cap = cv2.VideoCapture(DEVICE_ID, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("Error: Could not open device /dev/video{}".format(DEVICE_ID))
        exit(1)

    # Force resolution, format and FPSs
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDHT)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)

    # Verify configuration values
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print("Applied parameters -> Resolution: {}x{} | FPS: {}".format(actual_width, actual_height, actual_fps))

    # Set video writer (FourCC 'XVID' or 'MJPG' for AVI container)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, TARGET_FPS, (VIDEO_WIDHT, VIDEO_HEIGHT))

    if not out.isOpened():
        print("Error: Could not initialize VideoWriter")
        cap.release()
        exit(1)

    return output_path, cap, out


def start_recording(output_path, cap, out):
    print("Starting recording at: {}".format(output_path))

    # Comunication between threads con security limit
    q = Queue(maxsize=128)
    stopped = False

    # Producer thread: reads frames from camera without pauses
    def reader_thread():
        nonlocal stopped

        while not stopped:
            ret.frame = cap.read()
            if not ret:
                stopped = True
                break

            # If queue is full, discard oldest frame
            if q.full():
                try:
                    q.get_nowait()
                except Empty:
                    pass

            q.put(frame)

    # Start reader_thread
    t = Thread(target=reader_thread, daemon=True)
    t.start()

    frame_count = 0
    star_time = time.time()

    try:
        while not stopped:
            try:
                frame = q.get(timeout=0.05)
                out.write(frame)
                frame_count += 1

            except Empty:
                continue

    except Exception:
        print("Stopping recording...")

    finally:
        stopped = True
        t.join(timeout=1.0)
        
        end_time = time.time()
        duration = end_time - star_time
        cap.release()
        out.release()

        print("\n--- Statistics ---")
        print("Total frames: {}".format(frame_count))
        print(f"Effective duration: {duration:.2f} seconds")
        if duration > 0:
            print(f"Average FPS: {frame_count / duration:.2f}")

        print("File saved at: {}".format(output_path))


if __name__ == "__main__":
    output_path, cap, out = setup()

    start_recording(output_path, cap, out)
