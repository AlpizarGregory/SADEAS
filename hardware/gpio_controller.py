from gpiozero import LED

from constants import PIN_GREEN_LED, PIN_RED_LED

# Hardware definition
green_led = LED(PIN_GREEN_LED)
red_led = LED(PIN_RED_LED)


def notify_success():
    green_led.on()
    red_led.off()


def notify_failure_or_waiting():
    red_led.on()
    green_led.off()
