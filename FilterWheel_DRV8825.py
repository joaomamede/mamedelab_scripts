#------------------------------------------------------------------------------#
import RPi.GPIO as GPIO
from time import sleep
# import the library
from RpiMotorLib import RpiMotorLib

#define GPIO pins
GPIO_pins = (2,3,4) # Microstep Resolution MS1-MS3 -> GPIO Pin
direction= 20       # Direction -> GPIO Pin
step = 21      # Step -> GPIO Pin

# Declare an named instance of class pass GPIO pins numbers
mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "DRV8825")
#43full
adjacent = 688
#steps from HAL detection to position 0.
fromcal_to0 = 380
speed = 0.0005813953488372093
hal = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(hal, GPIO.IN)

# (Full, Half, 1/4, 1/8, 1/16)
steptype = '1/16'
#The main method that moves motor is called motor_go, takes 6 inputs.
#motor_go(clockwise, steptype, steps, stepdelay, verbose, initdelay):
# call the function, pass the arguments
calspeed = 0.5/adjacent
def calibrate():
    while GPIO.input(hal) == GPIO.HIGH:
        mymotortest.motor_go(False, steptype ,16, calspeed, False, 0.00001)
    sleep(1)
    mymotortest.motor_go(False, steptype , fromcal_to0, calspeed, False, .0005)



calibrate()

mymotortest.motor_go(True, steptype , adjacent, .0001, False, .05)
#50ms to start for adjacent
speed = 0.05/adjacent
#30ms to start
speed = 0.03/adjacent
#25ms to start
# speed = 0.025/adjacent
#10ms for adjacent
maxspeed = 0.02/adjacent
#8ms for adjancet
# maxspeed = 0.08/adjacent
import time

start = time.time()
print("hello")
multiplier = 1.5
#
# speed = 3.633720930232558e-04
speedtemp = speed
shootspeed = 0.042
for i in range(16):
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8*2:
        mymotortest.motor_go(False, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//16]*8*2:
        mymotortest.motor_go(False, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//18]*8:
        mymotortest.motor_go(True, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype , accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype , accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)

end = time.time()
print(end - start)
# good practise to cleanup GPIO at some point before exit


GPIO.cleanup()
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
import RPi.GPIO as GPIO
from time import sleep
# import the library
from RpiMotorLib import RpiMotorLib

#define GPIO pins
GPIO_pins = (2,3,4) # Microstep Resolution MS1-MS3 -> GPIO Pin
direction= 20       # Direction -> GPIO Pin
step = 21      # Step -> GPIO Pin

# Declare an named instance of class pass GPIO pins numbers
mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "DRV8825")
#43full
adjacent = 43
#steps from HAL detection to position 0.
fromcal_to0 = 24
speed = 0.05/adjacent
hal = 27
GPIO.setup(hal, GPIO.IN)

# (Full, Half, 1/4, 1/8, 1/16)
steptype = 'Full'
#The main method that moves motor is called motor_go, takes 6 inputs.
#motor_go(clockwise, steptype, steps, stepdelay, verbose, initdelay):
# call the function, pass the arguments
calspeed = 0.1/adjacent
def calibrate():
    while GPIO.input(hal) == GPIO.HIGH:
        mymotortest.motor_go(False, steptype ,1 calspeed, False, 0.00001)
    sleep(1)
    mymotortest.motor_go(False, steptype , fromcal_to0, calspeed, False, .0005)



calibrate()

mymotortest.motor_go(True, steptype , adjacent, .0001, False, .05)
#50ms to start for adjacent
speed = 0.05/adjacent
#30ms to start
speed = 0.03/adjacent
#25ms to start
# speed = 0.025/adjacent
#10ms for adjacent
maxspeed = 0.02/adjacent
#8ms for adjancet
# maxspeed = 0.08/adjacent
import time

start = time.time()
print("hello")
multiplier = 1.5
#
# speed = 3.633720930232558e-04
speedtemp = speed
shootspeed = 0.042
for i in range(16):
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8*2:
        mymotortest.motor_go(False, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//16]*8*2:
        mymotortest.motor_go(False, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//18]*8:
        mymotortest.motor_go(True, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype , accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype , accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)

end = time.time()
print(end - start)
# good practise to cleanup GPIO at some point before exit


GPIO.cleanup()
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
import RPi.GPIO as GPIO
from time import sleep
# import the library
from RpiMotorLib import RpiMotorLib

#define GPIO pins
GPIO_pins = (2,3,4) # Microstep Resolution MS1-MS3 -> GPIO Pin
direction= 20       # Direction -> GPIO Pin
step = 21      # Step -> GPIO Pin

# Declare an named instance of class pass GPIO pins numbers
mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "DRV8825")
#43full
adjacent = 43*32
#steps from HAL detection to position 0.
fromcal_to0 = 24*32
speed = 0.0005813953488372093
hal = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(hal, GPIO.IN)

# (Full, Half, 1/4, 1/8, 1/16,1/32)
steptype = '1/32'
#The main method that moves motor is called motor_go, takes 6 inputs.
#motor_go(clockwise, steptype, steps, stepdelay, verbose, initdelay):
# call the function, pass the arguments
calspeed = 0.5/adjacent
def calibrate():
    while GPIO.input(hal) == GPIO.HIGH:
        mymotortest.motor_go(False, steptype ,1*32, calspeed, False, 0.00001)
    sleep(1)
    mymotortest.motor_go(False, steptype , fromcal_to0, calspeed, False, .0005)



calibrate()

mymotortest.motor_go(True, steptype , adjacent, .0001, False, .05)
#50ms to start for adjacent
speed = 0.05/adjacent
#30ms to start
speed = 0.03/adjacent
#25ms to start
# speed = 0.025/adjacent
#10ms for adjacent
maxspeed = 0.02/adjacent
#8ms for adjancet
# maxspeed = 0.08/adjacent
import time

start = time.time()
print("hello")
multiplier = 1.5
#
# speed = 3.633720930232558e-04
speedtemp = speed
shootspeed = 0.042
for i in range(16):
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8*2:
        mymotortest.motor_go(False, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//16]*8*2:
        mymotortest.motor_go(False, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//18]*8:
        mymotortest.motor_go(True, steptype, accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)
    speedtemp = speed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype , accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp /multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    for accsteps in [int(adjacent)//16]*8:
        mymotortest.motor_go(True, steptype , accsteps, speedtemp, False, 1e-6)
        speedtemp = speedtemp *multiplier
        if speedtemp <- maxspeed:
            speedtemp = maxspeed
    sleep(shootspeed)

end = time.time()
print(end - start)
# good practise to cleanup GPIO at some point before exit


GPIO.cleanup()
#------------------------------------------------------------------------------#
