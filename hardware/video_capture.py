import subprocess
import datetime
import os
import time

from gpiozero import LED

from gpio_controller import notify_failure_or_waiting, notify_success
from constants import (
    RETRY_DELAY, 
    VIDEO_DEVICE, 
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    TARGET_FPS,
    OUTPUT_FOLDER,
    SEGMENT_DURATION
)


def record_video():
    """
    Records a video segment using FFmpeg.
    The camera's MJPEG stream is copied without re-encoding.
    """

    # Ensure the output directory exists and is writable.
    if not os.path.isdir(OUTPUT_FOLDER):
        notify_failure_or_waiting()
        print(f"Output directory not found: {OUTPUT_FOLDER}")
        time.sleep(RETRY_DELAY)
        return

    if not os.access(OUTPUT_FOLDER, os.W_OK):
        notify_failure_or_waiting()
        print(f"Output directory is not writable: {OUTPUT_FOLDER}")
        time.sleep(RETRY_DELAY)
        return

    if not os.path.exists(VIDEO_DEVICE):
        notify_failure_or_waiting()
        print(f"Camera not found: {VIDEO_DEVICE}")
        time.sleep(RETRY_DELAY)
        return

    notify_success()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    output_file = os.path.join(
        OUTPUT_FOLDER,
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
        "-t", str(SEGMENT_DURATION),
        "-map", "0:v:0",
        "-c:v", "copy",
        "-f", "matroska",
        output_file,
    ]

    print(f"\nStarting recording: {output_file}")
    print(f"Resolution requested: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"Frame rate requested: {TARGET_FPS} FPS")
    print(f"Segment duration: {SEGMENT_DURATION} seconds")

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
        notify_failure_or_waiting()
        print("\nRecording interrupted by user.")
        raise

    except OSError as error:
        notify_failure_or_waiting()
        print(f"Could not execute FFmpeg: {error}")
        time.sleep(RETRY_DELAY)

