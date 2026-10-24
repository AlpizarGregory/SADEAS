import cv2
import time
import os

# Capture parameters
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
TARGET_FPS = 15.0
DEVICE_ID = 0  # /dev/video0

# Videos directory
OUTPUT_DIR = "/home/alpizargregory/sadeas_videos"


def setup():
    print("Starting setup")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(
        OUTPUT_DIR,
        f"sadeas_capture_{timestamp}.avi"
    )

    # Initialize V4L2 capture
    cap = cv2.VideoCapture(DEVICE_ID, cv2.CAP_V4L2)

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open camera /dev/video{DEVICE_ID}"
        )

    # Request MJPEG before setting resolution and FPS
    cap.set(
        cv2.CAP_PROP_FOURCC,
        cv2.VideoWriter_fourcc(*"MJPG")
    )
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)

    # Request a small capture buffer when supported
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Verify actual configuration
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)

    actual_fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    fourcc_text = "".join(
        chr((actual_fourcc >> (8 * i)) & 0xFF)
        for i in range(4)
    )

    print(
        f"Camera: {actual_width}x{actual_height}, "
        f"{actual_fps:.2f} FPS, format: {fourcc_text}"
    )

    if (actual_width, actual_height) != (
        VIDEO_WIDTH, VIDEO_HEIGHT
    ):
        cap.release()
        raise RuntimeError(
            "The camera did not accept the requested resolution"
        )

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")

    out = cv2.VideoWriter(
        output_path,
        fourcc,
        TARGET_FPS,
        (VIDEO_WIDTH, VIDEO_HEIGHT)
    )

    if not out.isOpened():
        cap.release()
        raise RuntimeError("Could not initialize VideoWriter")

    return output_path, cap, out


def start_recording(output_path, cap, out):
    print(f"Recording to: {output_path}")
    print("Press Ctrl+C to stop recording.")

    frame_count = 0
    failed_reads = 0
    total_read_time = 0.0
    total_write_time = 0.0

    start_time = time.perf_counter()
    last_report_time = start_time

    try:
        while True:
            # Measure capture time
            read_start = time.perf_counter()
            ret, frame = cap.read()
            read_elapsed = time.perf_counter() - read_start

            total_read_time += read_elapsed

            if not ret:
                failed_reads += 1
                print("Warning: could not read frame")

                # Stop if the camera fails repeatedly
                if failed_reads >= 5:
                    print("Too many consecutive capture failures.")
                    break

                time.sleep(0.05)
                continue

            failed_reads = 0

            # Validate frame dimensions
            if frame.shape[1] != VIDEO_WIDTH or \
               frame.shape[0] != VIDEO_HEIGHT:
                print(
                    f"Unexpected frame size: "
                    f"{frame.shape[1]}x{frame.shape[0]}"
                )
                break

            # Measure writing time
            write_start = time.perf_counter()
            out.write(frame)
            total_write_time += time.perf_counter() - write_start

            frame_count += 1

            # Report progress every 5 seconds
            now = time.perf_counter()

            if now - last_report_time >= 5.0:
                elapsed = now - start_time
                effective_fps = frame_count / elapsed

                print(
                    f"Frames: {frame_count} | "
                    f"Elapsed: {elapsed:.1f}s | "
                    f"Effective FPS: {effective_fps:.2f}"
                )

                last_report_time = now

    except KeyboardInterrupt:
        print("\nRecording interrupted by user.")

    finally:
        duration = time.perf_counter() - start_time

        cap.release()
        out.release()

        print("\n--- Recording statistics ---")
        print(f"Total frames: {frame_count}")
        print(f"Real duration: {duration:.2f} seconds")

        if duration > 0:
            print(
                f"Effective FPS: "
                f"{frame_count / duration:.2f}"
            )

        if frame_count > 0:
            print(
                f"Average capture time: "
                f"{1000 * total_read_time / frame_count:.2f} ms"
            )
            print(
                f"Average write time: "
                f"{1000 * total_write_time / frame_count:.2f} ms"
            )

        print(f"Configured playback FPS: {TARGET_FPS:.2f}")
        print(f"Video saved at: {output_path}")


if __name__ == "__main__":
    output_path, cap, out = setup()
    start_recording(output_path, cap, out)