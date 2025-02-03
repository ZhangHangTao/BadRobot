# utils_robot.py

import socket
import cv2
import numpy as np
import time
from utils_pump import *
import os
from pyorbbecsdk import *
from utils import frame_to_bgr_image
p = 3.1415926535


class UR:
    def __init__(self, host, port=30003):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(1)
        self.socket.connect((self.host, self.port))
        print("Connected to robot")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            print("Disconnected from robot")

    def send_command(self, command):
        if self.socket:
            self.socket.send((command + "\n").encode())
            print(f"Sent command: {command}")

    def catch_on(self):
        command = f"set_tool_digital_out(0,True)"
        self.send_command(command)
        
    def catch_off(self):
        command = f"set_tool_digital_out(0,False)"
        self.send_command(command)
        
    def pump_on(self):
        command = f"set_standard_digital_out(5,True)"
        self.send_command(command)
        
    def pump_off(self):
        command = f"set_standard_digital_out(5,False)"
        self.send_command(command)
        time.sleep(0.2)
        
        command = f"set_standard_digital_out(5,True)"
        self.send_command(command)
        time.sleep(0.01)
        
        command = f"set_standard_digital_out(5,False)"
        self.send_command(command)
        time.sleep(0.2)
        

        
    def movej(self, q, a=0.3, v=0.3, t=0, r=0):
        command = f"movej({q}, a={a}, v={v}, t={t}, r={r})"
        self.send_command(command)

    def movel(self, pose, a=0.05, v=0.05):
        command = f"movel([{pose[0]},{pose[1]},{pose[2]},{pose[3]},{pose[4]},{pose[5]}], a={a}, v={v})"
        self.send_command(command)

    def move_to_z(self, new_z):

        command = (
            "def move_to_z():\n"
            "  pose = get_actual_tcp_pose()\n"
            f"  pose[2] = {new_z}\n"
            "  movel(pose, a=0.05, v=0.05)\n"
            "end\n"
        )
        self.send_command(command)

    def move_to_xyz(self, new_x, new_y, new_z):

        command = (
            "def move_to_xyz():\n"
            "  pose = get_actual_tcp_pose()\n"
            f"  pose[0] = {new_x}\n"
            f"  pose[1] = {new_y}\n"
            f"  pose[2] = {new_z}\n"
            "  movel(pose, a=0.1, v=0.1)\n"
            "end\n"
        )
        self.send_command(command)

    def stop(self):
        command = "stopj(2)"
        self.send_command(command)


robot = UR("192.168.1.108")
robot.connect()



def back_zero():

    robot.movej([-135/180*p, -90/180*p, 60/180*p, -150/180*p, 90/180*p, 0], a=1, v=2)
    time.sleep(0.3)

def relax_arms():
    print('1')
    #mc.release_all_servos()

def head_shake():
    print('shake')

    #mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    #time.sleep(1)
    #for count in range(2):
        #mc.send_angle(5, 30, 80)
        #time.sleep(0.5)
        #mc.send_angle(5, -30,80)
        #time.sleep(0.5)
    # mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    # time.sleep(1)
    #mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    #time.sleep(2)

def head_dance():
    print('dance')

    #mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    #time.sleep(1)
    #for count in range(1):
        #mc.send_angles([(-0.17),(-94.3),118.91,(-39.9),59.32,(-0.52)],80)
        #time.sleep(1.2)
        #mc.send_angles([67.85,(-3.42),(-116.98),106.52,23.11,(-0.52)],80)
        #time.sleep(1.7)
        #mc.send_angles([(-38.14),(-115.04),116.63,69.69,3.25,(-11.6)],80)
        #time.sleep(1.7)
        #mc.send_angles([2.72,(-26.19),140.27,(-110.74),(-6.15),(-11.25)],80)
        #time.sleep(1)
        #mc.send_angles([0,0,0,0,0,0],80)

def head_nod():
    print('nod')

    #mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    #for count in range(2):
        #mc.send_angle(4, 13, 70)
        #time.sleep(0.5)
        #mc.send_angle(4, -20, 70)
        #time.sleep(1)
        #mc.send_angle(4,13,70)
        #time.sleep(0.5)
    #mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)

def move_to_coords(X=150, Y=-130, HEIGHT=200):

    robot.move_to_xyz(X/1000, Y/1000, HEIGHT/1000)


def move_z(Z=150):

    robot.move_to_z(Z/1000)

def catch(t='pump',z=1):
    if t=='pump':
        if z==0:
            robot.pump_off()
        elif z==1:
            robot.pump_on()
    elif t=='catch':
        if z==0:
            robot.catch_off()
        elif z==1:
            robot.catch_on()

    else:
        print('error')
 
    
def single_joint_move(joint_index, angle):
    print('angle'.format(joint_index, angle))
    #mc.send_angle(joint_index, angle, 40)
    #time.sleep(2)

def move_to_top_view():
    #robot.movej([-258.82/180*p, -75.32/180*p, -57.42/180*p, -134.59/180*p, 90/180*p, 56.5/180*p], a=2, v=3)
    robot.movej([90/180*p, -88.53/180*p, -54.14/180*p, -127.2/180*p, 90/180*p, 0/180*p], a=2, v=3)
    time.sleep(4)




def save_one_color_frame(frame: ColorFrame, filename="temp/vl_now.jpg"):
    if frame is None:
        print("No frame to save.")
        return
    image = frame_to_bgr_image(frame)
    if image is None:
        print("Failed to convert frame to image.")
        return
    cv2.imwrite(filename, image)
    print(f"Image saved as {filename}")

def capture_and_save_image(filename="temp/vl_now.jpg", timeout=800):
    pipeline = Pipeline()
    config = Config()

    try:
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if profile_list is not None:
            color_profile: VideoStreamProfile = profile_list.get_default_video_stream_profile()
            config.enable_stream(color_profile)
    except OBError as e:
        print(f"Error getting stream profile list: {e}")
        return None

    pipeline.start(config)
    
    try:
        frames = pipeline.wait_for_frames(timeout)
        if frames is not None:
            color_frame = frames.get_color_frame()
            if color_frame is not None:
                save_one_color_frame(color_frame, filename)
                return frame_to_bgr_image(color_frame)
        else:
            print("No frames received.")
            return None
    except Exception as e:
        print(f"An error occurred while capturing the frame: {e}")
        return None
    finally:
        pipeline.stop()

def top_view_shot(check=False):


    move_to_top_view()


    img_bgr = capture_and_save_image()
    if img_bgr is not None:

        cv2.destroyAllWindows()
        cv2.imshow('vlm', img_bgr)
        
        if check:

            while(True):
                key = cv2.waitKey(10) & 0xFF
                if key == ord('c'):
                    break
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    raise NameError('q')
        else:
            if cv2.waitKey(10) & 0xFF == None:
                pass
    else:
        print("Failed to capture image.")


    cv2.destroyAllWindows()




def linear_interpolate(x, x_points, y_points):

    x0, x1 = x_points
    y0, y1 = y_points


    slope = (y1 - y0) / (x1 - x0)
    

    return y0 + slope * (x - x0)


def eye2hand(X_im=160, Y_im=120):


    cali_1_im = [502, 312]
    cali_1_mc = [19.38, 416.17]
    cali_2_im = [858, 121]
    cali_2_mc = [260.4, 529.78]
    
    X_cali_im = [cali_1_im[0], cali_2_im[0]]
    X_cali_mc = [cali_1_mc[0], cali_2_mc[0]]
    Y_cali_im = [cali_2_im[1], cali_1_im[1]]
    Y_cali_mc = [cali_2_mc[1], cali_1_mc[1]]


    X_mc = linear_interpolate(X_im, X_cali_im, X_cali_mc)
    Y_mc = linear_interpolate(Y_im, Y_cali_im, Y_cali_mc)

    return X_mc, Y_mc




def pump_move(XY_START=[230,-50], HEIGHT_START=65, XY_END=[100,220], HEIGHT_END=100, HEIGHT_SAFE=120):
    #catch('catch',0)
    catch('pump', 0)



    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(20, GPIO.OUT)
    #GPIO.setup(21, GPIO.OUT)


    #mc.set_fresh_mode(0)
    

    # mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    # time.sleep(4)
    


    #time.sleep(3)
    #print(XY_START[0])
    #print(XY_START[1])
    move_to_coords(XY_START[0],XY_START[1],HEIGHT_SAFE)
    time.sleep(6)
    #mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 20, 0)
    #time.sleep(3)

    

    print(HEIGHT_START)
    #mc.send_coords([XY_START[0], XY_START[1], HEIGHT_START, 0, 180, 90], 15, 0)
    move_z(HEIGHT_START+3)
    time.sleep(4)
    catch('pump', 1)
    time.sleep(1)

    move_z(HEIGHT_SAFE)
    #mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(5)



    #print(XY_END[0])
    #print(XY_END[1])
    move_to_coords(XY_END[0],XY_END[1],HEIGHT_SAFE)
    #mc.send_coords([XY_END[0], XY_END[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(5)


    #mc.send_coords([XY_END[0], XY_END[1], HEIGHT_END, 0, 180, 90], 20, 0)
    move_z(HEIGHT_END+50)
    time.sleep(4)
    catch('pump', 0)
    time.sleep(1)



