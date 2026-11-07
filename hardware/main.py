import time

from video_capture import record_video, hardware_verification
from gpio_controller import notify_failure_or_waiting, button, notify_start_recording

def main():
    print("SADEAS video capture started.")
    print("Press Ctrl+C to stop.")


    able_to_record = False

    while not able_to_record:
        notify_failure_or_waiting()
        able_to_record = hardware_verification()
        time.sleep(1)

    button.wait_for_press()

    notify_start_recording()
    try:
        while True:
            record_video()
            time.sleep(1)

    except KeyboardInterrupt:
        notify_failure_or_waiting()
        print("\nSADEAS video capture stopped.")

if __name__ == "__main__":
    main()
