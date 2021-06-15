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
    lastFound = 0
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
    arucoParams = cv2.aruco.DetectorParameters_create()
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        mc.start_turn_left(15)
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
                    print('overshot')
                    mc.stop()
                    mc.start_turn_right(15)
                elif corners[0][0][1][0] < (camera_width / 2) + 10:
                    print('other overshoot')
                    mc.stop()
                    mc.start_turn_left(15)
                else:
                    print('centred')
                    mc.stop()
                    if corners[0][0][1][0] - corners[0][0][0][0] < 50:
                        print('Moving Closer')
                        mc.start_forward(0.5)
                    elif corners[0][0][1][0] - corners[0][0][0][0] > 50:
                        print('Backing Up')
                        mc.start_back(0.1)
                    else:
                        mc.stop()
                        print('Optimal distance')
                        target_found = True
            else:
                lastFound += 1

            if lastFound > 50:
                print('Target Lost')
                mc.start_turn_left(15)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


            # if len(corners) > 0:
            #     print("Detected Marker")
            #     # flatten the ArUco IDs list
            #     ids = ids.flatten()
            #     if 1 in ids:
            #         index = ids.index(1)
            #         target = corners[index]
            #         if target[1][1] < (camerawidth/2 + 10):
            #             print('Overshot')
            #             mc.start_turn_right(rate=0.1)
            #
            #     cv2.imshow('frame', frame)
                # loop over the detected ArUCo corners
                # for (markerCorner, markerID) in zip(corners, ids):
                #     # extract the marker corners (which are always returned in
                #     # top-left, top-right, bottom-right, and bottom-left order)
                #     corners = markerCorner.reshape((4, 2))
                #     (topLeft, topRight, bottomRight, bottomLeft) = corners
                #     # convert each of the (x, y)-coordinate pairs to integers
                #     topRight = (int(topRight[0]), int(topRight[1]))
                #     bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                #     bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                #     topLeft = (int(topLeft[0]), int(topLeft[0]))







if __name__ == '__main__':
    cflib.crtp.init_drivers()


    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        cap = cv2.VideoCapture(2)

        scf.cf.param.add_update_callback(group="deck", name="bcFlow2", cb=param_deck_flow)

        time.sleep(1)
        #simple_connect()
        #move_lin_simp(scf)
        #test_flight(scf)
        find_target(scf, cap)
