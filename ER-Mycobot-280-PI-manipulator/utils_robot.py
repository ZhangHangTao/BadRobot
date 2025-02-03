print('Import the robotic arm connection module.')

from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD
import cv2
import numpy as np
import time
from utils_pump import *


mc = MyCobot(PI_PORT, PI_BAUD)
mc.set_fresh_mode(0)

import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)

def back_zero():
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

def relax_arms():
    mc.release_all_servos()

def head_shake():
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    time.sleep(1)
    for count in range(2):
        mc.send_angle(5, 30, 80)
        time.sleep(0.5)
        mc.send_angle(5, -30,80)
        time.sleep(0.5)
    # mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    # time.sleep(1)
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(2)

def head_dance():
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    time.sleep(1)
    for count in range(1):
        mc.send_angles([(-0.17),(-94.3),118.91,(-39.9),59.32,(-0.52)],80)
        time.sleep(1.2)
        mc.send_angles([67.85,(-3.42),(-116.98),106.52,23.11,(-0.52)],80)
        time.sleep(1.7)
        mc.send_angles([(-38.14),(-115.04),116.63,69.69,3.25,(-11.6)],80)
        time.sleep(1.7)
        mc.send_angles([2.72,(-26.19),140.27,(-110.74),(-6.15),(-11.25)],80)
        time.sleep(1)
        mc.send_angles([0,0,0,0,0,0],80)

def head_nod():
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    for count in range(2):
        mc.send_angle(4, 13, 70)
        time.sleep(0.5)
        mc.send_angle(4, -20, 70)
        time.sleep(1)
        mc.send_angle(4,13,70)
        time.sleep(0.5)
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)

def move_to_coords(X=150, Y=-130, HEIGHT_SAFE=230):
    mc.send_coords([X, Y, HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(4)

def single_joint_move(joint_index, angle):
    mc.send_angle(joint_index, angle, 40)
    time.sleep(2)

def move_to_top_view():
    #mc.send_angles([-62.13, 8.96, -87.71, -14.41, 2.54, -16.34], 10)
    mc.send_angles([-62.13, 7.82, -75.49,-15.73,-1.66,-15.99],20)
    #mc.send_angles([20, -25, -9, -54, 0, -25], 10)
    time.sleep(3)

def top_view_shot(check=False):
    move_to_top_view()
    cap = cv2.VideoCapture(0)
    cap.open(0)
    time.sleep(0.3)
    success, img_bgr = cap.read()

    cv2.imwrite('temp/vl_now.jpg', img_bgr)

    cv2.destroyAllWindows()
    cv2.imshow('vlm', img_bgr)
    if check:
        print('Please confirm the photo was taken successfully. Press c to continue, press q to quit.')
        while(True):
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'):
                break
            if key == ord('q'):
                # exit()
                cv2.destroyAllWindows()
                raise NameError('press q to quit')
    else:
        if cv2.waitKey(10) & 0xFF == None:
            pass

    cap.release()

def eye2hand(X_im=160, Y_im=120):
    '''
    Input the pixel coordinates of the target point in the image, convert them to robotic arm coordinates.
    '''

    # Organize the coordinates of the two calibration points.
    cali_1_im = [125,302]                   # Bottom left corner, the pixel coordinates of the first calibration point, need to be filled in manually!
    cali_1_mc = [-16,-220]
    cali_2_im = [441.4,139]               # Top right corner, the pixel coordinates of the second calibration point, need to be filled in manually!
    cali_2_mc = [129,-145]
    
    X_cali_im = [cali_1_im[0], cali_2_im[0]]     # Pixel coordinates.
    X_cali_mc = [cali_1_mc[0], cali_2_mc[0]]     # Robotic arm coordinates.
    Y_cali_im = [cali_2_im[1], cali_1_im[1]]     # Pixel coordinates.
    Y_cali_mc = [cali_2_mc[1], cali_1_mc[1]]     # Robotic arm coordinates.

    X_mc = int(np.interp(X_im, X_cali_im, X_cali_mc))

    Y_mc = int(np.interp(Y_im, Y_cali_im, Y_cali_mc))

    return X_mc, Y_mc

def pump_move(mc, XY_START=[230,-50], HEIGHT_START=65, XY_END=[100,220], HEIGHT_END=100, HEIGHT_SAFE=220):

    '''
    mc: Robotic arm instance
    XY_START: Starting robotic arm coordinates
    HEIGHT_START: Starting height 90
    XY_END: Ending robotic arm coordinates
    HEIGHT_END: Ending height
    HEIGHT_SAFE: Safe height during transportation
    '''

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)

    mc.set_fresh_mode(0)

    print(XY_START[0])
    print(XY_START[1])
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(3)

    pump_on()

    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_START, 0, 180, 90], 15, 0)
    time.sleep(3)

    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(3)

    print(XY_END[0])
    print(XY_END[1])
    mc.send_coords([XY_END[0], XY_END[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(3)

    mc.send_coords([XY_END[0], XY_END[1], HEIGHT_END, 0, 180, 90], 20, 0)
    time.sleep(3)

    pump_off()

    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)


def pump_move_collision(mc, XY_START=[230, -50], HEIGHT_START=65, XY_END=[100, 220], HEIGHT_END=100, HEIGHT_SAFE=220):
    '''
    mc: Robotic arm instance
    XY_START: Starting robotic arm coordinates
    HEIGHT_START: Starting height
    XY_END: Ending robotic arm coordinates
    HEIGHT_END: Ending height
    HEIGHT_SAFE: Safe height during transportation
    '''

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)

    # Set motion mode to interpolation
    mc.set_fresh_mode(0)

    # # Reset robotic arm to zero
    # print('    Reset robotic arm to zero')
    # mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    # time.sleep(4)

    # Move suction pump above the object
    print('    Move suction pump above the object')
    print(XY_START[0])
    print(XY_START[1])
    mc.send_coords([XY_START[0] + 58, XY_START[1] + 40, HEIGHT_SAFE, 0, 180, 90], 10, 0)
    time.sleep(3)

    # Turn on suction pump
    pump_on()

    # Move suction pump down to grab the object
    print('    Move suction pump down to grab the object')
    mc.send_coords([XY_START[0] + 58, XY_START[1] + 40, HEIGHT_START, 0, 180, 90], 10, 0)
    time.sleep(3)

    # Lift the object
    print('    Lift the object')
    mc.send_coords([XY_START[0] + 58, XY_START[1] + 40, HEIGHT_SAFE, 0, 180, 90], 10, 0)
    time.sleep(3)

    # Move the object above the target
    print('    Move the object above the target')
    print(XY_END[0])
    print(XY_END[1])
    mc.send_coords([XY_END[0] - 10, XY_END[1] + 110, HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(3)

    # Lower the object down
    print('    Lower the object down')
    mc.send_coords([XY_END[0] - 10, XY_END[1] + 110, HEIGHT_END, 0, 180, 90], 90, 0)
    time.sleep(5)

    # Move forward to perform a collision
    print('    Move forward to perform a collision')
    mc.send_coords([XY_END[0] - 10, XY_END[1], HEIGHT_END + 50, 0, 180, 90], 90, 0)
    time.sleep(3)

    # Turn off suction pump
    pump_off()

    # Reset robotic arm to zero
    print('    Reset robotic arm to zero')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

