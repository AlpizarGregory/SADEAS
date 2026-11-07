from gpiozero import LED, Button
from time import sleep

from constants import PIN_GREEN_LED, PIN_RED_LED, PIN_BUTTON

# Hardware definition
green_led = LED(PIN_GREEN_LED)
red_led = LED(PIN_RED_LED)
button = Button(PIN_BUTTON, pull_up=True, bounce_time=0.05)


def notify_success():
    green_led.on()
    red_led.off()


def notify_failure_or_waiting():
    red_led.on()
    green_led.off()


def notify_start_recording():
    for _ in range(5):
        green_led.on()
        sleep(0.5)
        green_led.off()
        sleep(0.5)
