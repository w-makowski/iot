#!/usr/bin/env python3

from config import *
import RPi.GPIO as GPIO

brightness = 50
brightness_step = 10

pwm_led = GPIO.PWM(led1, 50)

encoder_left_prev_state = GPIO.input(encoder_left)
encoder_right_prev_state = GPIO.input(encoder_right)

def encoder_callback(channel):
    global brightness, encoder_left_prev_state, encoder_right_prev_state

    encoder_left_state = GPIO.input(encoder_left)
    encoder_right_state = GPIO.input(encoder_right)

    if channel == encoder_left and encoder_left_prev_state == 1 and encoder_left_state == 0:
        brightness = max(0, brightness - brightness_step)

    if channel == encoder_right and encoder_right_prev_state == 1 and encoder_right_state == 0:
        brightness = min(100, brightness + brightness_step)
        
    pwm_led.ChangeDutyCycle(brightness)

    encoder_left_prev_state = encoder_left_state
    encoder_right_prev_state = encoder_right_state

def main():
    try:
        print("Press Ctrl+C to exit.")

        duty_cycle = 0
        pwm_led.start(duty_cycle)
        GPIO.add_event_detect(encoder_left, GPIO.FALLING, callback=encoder_callback, bouncetime=200)
        GPIO.add_event_detect(encoder_right, GPIO.FALLING, callback=encoder_callback, bouncetime=200)

        while True:
            pass

    except KeyboardInterrupt:
        print("\nExiting program.")
        
    finally:
        pwm_led.stop()
        GPIO.cleanup()

if __main__ == "__main__":
    main()
