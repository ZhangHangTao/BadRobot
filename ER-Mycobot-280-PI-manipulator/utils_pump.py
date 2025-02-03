print('Import the suction pump control module.')
import RPi.GPIO as GPIO
import time

# 初始化GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)

def pump_on():
    GPIO.output(20, 0)

def pump_off():
    GPIO.output(20, 1)
    time.sleep(0.05)
    GPIO.output(21, 0)
    time.sleep(0.2)
    GPIO.output(21, 1)
    time.sleep(0.05)
    GPIO.output(21, 0)
    time.sleep(0.2)
    GPIO.output(21, 1)
    time.sleep(0.05)