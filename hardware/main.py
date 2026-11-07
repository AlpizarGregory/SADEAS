import time

from video_capture import record_video
from gpio_controller import notify_failure_or_waiting

def main():
    print("SADEAS video capture started.")
    print("Press Ctrl+C to stop.")

    notify_failure_or_waiting()

    try:
        while True:
            record_video()
            time.sleep(1)

    except KeyboardInterrupt:
        notify_failure_or_waiting()
        print("\nSADEAS video capture stopped.")

if __name__ == "__main__":
    main()
