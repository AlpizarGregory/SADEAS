import subprocess
import datetime
import os
import time
import signal

# Configuration
OUTPUT_FOLDER = "/home/alpizargregory/sadeas_videos"
VIDEO_DEVICE = "/dev/video0"

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
TARGET_FPS = 30

SEGMENT_DURATION = 60  # seconds
RETRY_DELAY = 5        # seconds


def record_video(output_folder, duration):
    """
    Records a video segment using FFmpeg.
    The camera's MJPEG stream is copied without re-encoding.
    """

    # Ensure the output directory exists and is writable.
    if not os.path.isdir(output_folder):
        print(f"Output directory not found: {output_folder}")
        time.sleep(RETRY_DELAY)
        return

    if not os.access(output_folder, os.W_OK):
        print(f"Output directory is not writable: {output_folder}")
        time.sleep(RETRY_DELAY)
        return

    if not os.path.exists(VIDEO_DEVICE):
        print(f"Camera not found: {VIDEO_DEVICE}")
        time.sleep(RETRY_DELAY)
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    output_file = os.path.join(
        output_folder,
        f"video_{timestamp}.mkv"
    )

    command = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-f", "v4l2",
        "-input_format", "mjpeg",
        "-video_size", f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}",
        "-framerate", str(TARGET_FPS),
        "-i", VIDEO_DEVICE,
        "-t", str(duration),
        "-map", "0:v:0",
        "-c:v", "copy",
        "-f", "matroska",
        output_file,
    ]

    print(f"\nStarting recording: {output_file}")
    print(f"Resolution requested: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"Frame rate requested: {TARGET_FPS} FPS")
    print(f"Segment duration: {duration} seconds")

    try:
        result = subprocess.run(command, check=False)

        if result.returncode == 0:
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"Recording completed: {output_file}")
                print(f"File size: {size_mb:.2f} MiB")
            else:
                print("FFmpeg finished, but the output file is empty or missing.")

        elif result.returncode < 0:
            print(f"FFmpeg terminated by signal {-result.returncode}.")
        else:
            print(f"FFmpeg exited with error code {result.returncode}.")

    except KeyboardInterrupt:
        print("\nRecording interrupted by user.")
        raise

    except OSError as error:
        print(f"Could not execute FFmpeg: {error}")
        time.sleep(RETRY_DELAY)


def main():
    print("SADEAS video capture started.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            record_video(OUTPUT_FOLDER, SEGMENT_DURATION)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSADEAS video capture stopped.")


if __name__ == "__main__":
    main()
