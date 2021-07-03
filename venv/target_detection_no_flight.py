import cv2
import numpy as np

camera_width = 640
camera_height = 480

def find_target():
    target_found = False
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
    arucoParams = cv2.aruco.DetectorParameters_create()
    cap = cv2.VideoCapture(2)
    print('Start Search')
    lastFound = 0
    while not target_found:
        ret, frame = cap.read()
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
            if corners[0][0][0][1] < (camera_height / 2):
                print('Bottom Overshoot - Moving UP')
                zvelocity = 0.1
                centered_z = False
            elif corners[0][0][2][1] > (camera_height / 2):
                print('Top Overshoot - Moving DOWN')
                zvelocity = -0.1
                centered_z = False
            else:
                print('centred in z')
                zvelocity = 0.0
                centered_z = True
            if centered_yaw and centered_z:
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
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break




find_target()