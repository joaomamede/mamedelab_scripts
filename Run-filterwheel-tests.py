from time import sleep
import RPi.GPIO as GPIO

DIR = 20   # Direction GPIO Pin
STEP = 21  # Step GPIO Pin
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SPR = 260   # Steps per Revolution (360 / 7.5)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)


step_count = 43
delay = .002

for i in range(20):
GPIO.output(DIR, CW)
for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)

sleep(.5)
GPIO.output(DIR, CCW)
for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)

GPIO.cleanup()


import RPi.GPIO as GPIO
from time import sleep
# import the library
from RpiMotorLib import RpiMotorLib

#define GPIO pins
GPIO_pins = (2,3,48) # Microstep Resolution MS1-MS3 -> GPIO Pin
direction= 20       # Direction -> GPIO Pin
step = 21      # Step -> GPIO Pin

# Declare an named instance of class pass GPIO pins numbers
mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "A4988")
#43full
adjacent = 688
#steps from HAL detection to position 0.
fromcal_to0 = 395
speed = 3.633720930232558e-06
# (Full, Half, 1/4, 1/8, 1/16)
steptype = '1/16'
#The main method that moves motor is called motor_go, takes 6 inputs.
#motor_go(clockwise, steptype, steps, stepdelay, verbose, initdelay):
# call the function, pass the arguments
while GPIO.input(hal) == GPIO.HIGH:
    mymotortest.motor_go(False, steptype ,1 , .000001, False, )


mymotortest.motor_go(False, steptype , fromcal_to0, .001, False, .05)
mymotortest.motor_go(True, steptype , adjacent, .001, False, .05)
for i in range(20):
    mymotortest.motor_go(False, steptype, adjacent*2, speed, False, .005)
    sleep(0.042)
    mymotortest.motor_go(True, steptype, adjacent, speed, False, .005)
    sleep(0.042)
    mymotortest.motor_go(True, steptype , adjacent, speed, False, .005)
    sleep(0.042)
# good practise to cleanup GPIO at some point before exit
GPIO.cleanup()


import RPi.GPIO as GPIO

# import the library
from RpiMotorLib import RpiMotorLib

#define GPIO pins
GPIO_pins = (2,3,48) # Microstep Resolution MS1-MS3 -> GPIO Pin
direction= 20       # Direction -> GPIO Pin
step = 21      # Step -> GPIO Pin

# Declare an named instance of class pass GPIO pins numbers
mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "A4988")
#43full
adjacent = 688
# speed = 3.633720930232558e-05
speed = 1e-05
# (Full, Half, 1/4, 1/8, 1/16)
steptype = '1/16'
#The main method that moves motor is called motor_go, takes 6 inputs.
#motor_go(clockwise, steptype, steps, stepdelay, verbose, initdelay):
# call the function, pass the arguments
# mymotortest.motor_go(False, steptype , adjacent, .001, False, .05)

for i in range(10):
    mymotortest.motor_go(False, steptype , adjacent*2, speed, False, )
    sleep(0.042)
    mymotortest.motor_go(True, steptype, adjacent, speed, False, )
    sleep(0.042)
    mymotortest.motor_go(True, steptype , adjacent, speed, False,)
    sleep(0.042)
# good practise to cleanup GPIO at some point before exit
GPIO.cleanup()

import RPi.GPIO as GPIO

# import the library
from RpiMotorLib import RpiMotorLib

#define GPIO pins
GPIO_pins = (2,3,48) # Microstep Resolution MS1-MS3 -> GPIO Pin
direction= 20       # Direction -> GPIO Pin
step = 21      # Step -> GPIO Pin

# Declare an named instance of class pass GPIO pins numbers
mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "A4988")
#43full
adjacent = 43
speed = 1e-2
# (Full, Half, 1/4, 1/8, 1/16)
steptype = 'Full'
#The main method that moves motor is called motor_go, takes 6 inputs.
#motor_go(clockwise, steptype, steps, stepdelay, verbose, initdelay):
# call the function, pass the arguments
# mymotortest.motor_go(False, steptype , adjacent, .001, False, .05)

for i in range(10):
    mymotortest.motor_go(False, steptype , adjacent*2, speed, False,)
    sleep(0.042)
    mymotortest.motor_go(True, steptype, adjacent, speed, False,)
    sleep(0.042)
    mymotortest.motor_go(True, steptype , adjacent, speed, False,)
    sleep(0.042)
# good practise to cleanup GPIO at some point before exit
GPIO.cleanup()


import RPi.GPIO as GPIO

# import the library
from RpiMotorLib import RpiMotorLib

#define GPIO pins
GPIO_pins = (14, 15, 18) # Microstep Resolution MS1-MS3 -> GPIO Pin
direction= 20       # Direction -> GPIO Pin
step = 21      # Step -> GPIO Pin

# Declare a instance of class pass GPIO pins numbers and the motor type
mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "DRV8825")


# call the function, pass the arguments
mymotortest.motor_go(False, "Full" , 100, .01, False, .05)

# good practise to cleanup GPIO at some point before exit
GPIO.cleanup()
