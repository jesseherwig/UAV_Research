import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
import cv2
import numpy as np


uri = 'radio://0/80/2M/E7E7E7E7E7'
is_deck_attached = False
DEFAULT_HEIGHT = 0.5

camera_width = 640
camera_height = 480

def simple_connect():
    print("Connected")
    time.sleep(3)
    print("Disconnecting")

def param_deck_flow(name, value_str):
    value = int(value_str)
    print(value)
    global is_deck_attached
    if value:
        is_deck_attached = True
        print("Deck attached")
    else:
        is_deck_attached = False
        print("NO DECK NO DECK NO DECK")

def take_off_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(3)

def move_lin_simp(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)
        mc.forward(0.5)
        time.sleep(1)
        mc.turn_left(180)
        time.sleep(1)
        mc.forward(0.5)
        time.sleep(1)

def test_flight(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT, ) as mc:
        mc.start_turn_left()
        time.sleep(10)
        mc.start_turn_right(0.5)
        time.sleep(1)

def resize_targets(corners, ids):
    pass

def calculate_marker_pos(corners, ids):
    pass

def find_target(scf, vid):
    target_found = False
    centered_yaw = False
    centered_z = False
    centered_x = False
    
    lastFound = 0
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
    arucoParams = cv2.aruco.DetectorParameters_create()
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        xvelocity = 0.0
        zvelocity = 0.0
        yaw = -15
        print('start search')
        while(not target_found):
            ret, frame = vid.read()

            corners, ids, rejected = cv2.aruco.detectMarkers(frame, arucoDict,
                                                             parameters=arucoParams)
            frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), corners, ids)

            cv2.imshow('frame', frame_markers)

            if len(corners) > 0:
                lastFound = 0
                print('Detected marker')
                if corners[0][0][0][0] > (camera_width / 2) - 10:
                    print('Left Overshoot - Turning Right')
                    yaw = 15
                    centered_yaw = False
                elif corners[0][0][1][0] < (camera_width / 2) + 10:
                    print('Right Overshoot - Turning Left')
                    yaw = -15
                    centered_yaw = False
                else:
                    print('centred in yaw')
                    yaw = 0.0
                    centered_yaw = True
                if corners[0][0][0][1] < (camera_height / 2) + 10:
                    print('Bottom Overshoot - Moving UP')
                    zvelocity = 0.05
                    centered_z = False
                elif corners[0][0][2][1] > (camera_height / 2) - 10:
                    print('Top Overshoot - Moving DOWN')
                    zvelocity = -0.05
                    centered_z = False
                else:
                    print('centred in z')
                    zvelocity = 0.0
                    centered_z = True
                if centered_yaw and centered_z:
                    zvelocity = 0.0
                    yaw = 0.0
                    if corners[0][0][1][0] - corners[0][0][0][0] < 50:
                        print('Moving Closer')
                        xvelocity = 0.5
                    elif corners[0][0][1][0] - corners[0][0][0][0] > 50:
                        print('Backing Up')
                        xvelocity = -0.5
                    else:
                        xvelocity = 0.0
                        print('Optimal distance')
                        target_found = True
                else:
                    xvelocity = 0.0
            else:
                lastFound += 1

            if lastFound > 50:
                print('Target Lost')
                xvelocity = 0.0
                zvelocity = 0.0
                yaw = -15

            mc._set_vel_setpoint(xvelocity, 0.0, zvelocity, 0.0)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                mc.stop()
                break


if __name__ == '__main__':
    cflib.crtp.init_drivers()


    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        cap = cv2.VideoCapture(2)

        scf.cf.param.add_update_callback(group="deck", name="bcFlow2", cb=param_deck_flow)

        time.sleep(1)
        #simple_connect()
        #move_lin_simp(scf)
        #take_off_simple(scf)
        #test_flight(scf)
        find_target(scf, cap)

